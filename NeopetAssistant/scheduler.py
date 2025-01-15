import _G
import json
import jobs
from jobs.base_job import BaseJob
from errors import NeoError
from datetime import datetime

class JobScheduler:
    '''
    This class manages the execution of jobs.
    The jobs will executed concurrently with generators.
    '''
    def __init__(self, playwright, context, name='default'):
        self.pending_jobs = []
        self.queued_jobs = []
        self.current_job = None
        self.fiber = None
        self.running = False
        self.playwright = playwright
        self.pw = self.playwright
        self.context = context
        self.name = name
        self.job_returns = []

    def add_job(self, job):
        self.pending_jobs.append(job)

    def update(self):
        if not self.running:
            return
        if self.fiber:
            if not self.resume(self.fiber):
                self.stop_job(True)
            return
        # Copy queued jobs to pending jobs
        curt = datetime.now()
        curt_tz = datetime.now().astimezone()
        for job in self.queued_jobs:
            try:
                if job.next_run < curt:
                    _G.logger.info(f"Pending job {job.job_name}")
                    self.pending_jobs.append(job)
            except TypeError:
                if job.next_run < curt_tz:
                    _G.logger.info(f"Pending job {job.job_name}")
                    self.pending_jobs.append(job)
        # Pick highest priority pending job
        if self.pending_jobs:
            self.pending_jobs.sort(key=lambda x: x.priority, reverse=True)
            job = self.pending_jobs.pop(0)
            self.execute_job(job)
            return

    def execute_job(self, job):
        if not job:
            _G.logger.warning("No job to execute!")
            return
        _G.logger.info(f"Executing job: {job.job_name}")
        self.current_job = job
        self.current_job.set_context(self.context)
        self.fiber = job.start()

    def stop_job(self, queue_next:bool=True):
        if self.current_job:
            self.queue_job(self.current_job, queue_next)
            self.current_job = None
        self.fiber = None

    def resume(self, fiber):
        ret = None
        try:
            ret = next(fiber)
            if type(ret) == NeoError and ret.errno == 0:
                _G.logger.info("Job signaled return")
                job_ret = self.current_job.return_value
                if type(job_ret) != NeoError and job_ret.errno != 0:
                    self.job_returns.append(job_ret)
                self.stop_job()
                return False
        except StopIteration as ret:
            _G.logger.info("Job has stopped")
            job_ret = self.current_job.return_value or ret.value
            if type(job_ret) != NeoError and job_ret.errno != 0:
                self.job_returns.append(job_ret)
            self.stop_job()
            return False
        return True

    def queue_job(self, job, queue_next:bool=True):
        if queue_next:
            job.calc_next_run()
        self.queued_jobs.append(job)
        _G.logger.info(f"Queued job: {job.job_name}, next run: {job.next_run}")

    def start(self):
        _G.logger.info("Job scheduler started")
        self.running = True

    def stop(self, reason:str='manual stop'):
        _G.logger.warning(f"Job stopped: {reason}")
        self.running = False
        self.stop_job(queue_next=False)

    def save_status(self):
        _G.logger.info("Saving job scheduler status")
        savefile = f"./.job_scheduler_{self.name}.json"
        with open(savefile, 'w') as f:
            json.dump(self.to_dict(), f)

    def load_status(self, filename:str):
        _G.logger.info("Loading job scheduler status")
        with open(filename, 'r') as f:
            data = json.load(f)
            self.pending_jobs = []
            self.queued_jobs = []
            for job_data in data['pending_jobs']:
                job_module = getattr(jobs, job_data['name'])
                job_cls  = getattr(job_module, job_data['class'])
                job_instance = job_cls()
                job_instance.load_data(job_data)
                self.pending_jobs.append(job_instance)
            for job_data in data['queued_jobs']:
                job_module = getattr(jobs, job_data['name'])
                job_cls  = getattr(job_module, job_data['class'])
                job_instance = job_cls()
                job_instance.load_data(job_data)
                self.queued_jobs.append(job_instance)

    def to_dict(self):
        return {
            'name': self.name,
            'pending_jobs': [job.to_dict() for job in self.pending_jobs],
            'queued_jobs': [job.to_dict() for job in self.queued_jobs],
        }

    def terminate(self):
        _G.logger.info("Terminating job scheduler")
        self.stop('terminated')
        self.save_status()
        try:
            if self.context:
                self.context.close()
            self.playwright.stop()
        except Exception:
            pass