import _G
import json
import jobs
import os
from errors import NeoError
from datetime import datetime, timedelta

class JobScheduler:
    '''
    This class manages the execution of jobs.
    The jobs will executed concurrently with generators.
    '''
    def __init__(self, playwright, context, name='default', save_path='.',
                    idle_log_interval=60, job_pick_interval=10
                ):
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
        self.idle_log_interval = idle_log_interval
        self.last_idle_time = datetime.now() - timedelta(days=1)
        self.save_path = save_path
        self.job_pick_interval = job_pick_interval
        self.last_scan_time = datetime.now() - timedelta(days=1)

    def add_job(self, job):
        self.pending_jobs.append(job)

    def update(self):
        if not self.running:
            return
        if self.fiber:
            if not self.resume(self.fiber):
                self.stop_job(True)
            return
        if (datetime.now() - self.last_scan_time).total_seconds() < self.job_pick_interval:
            return
        self.last_scan_time = datetime.now()
        _G.log_debug("Picking up jobs")
        # Move queued jobs to pending jobs if ready
        curt = datetime.now()
        curt_tz = datetime.now().astimezone()
        unprocessed = []
        for job in self.queued_jobs:
            if not job.enabled or job == self.current_job:
                unprocessed.append(job)
                continue
            try:
                if job.next_run < curt:
                    _G.log_info(f"Pending job {job.job_name}")
                    self.add_job(job)
                    continue
            except TypeError:
                if job.next_run < curt_tz:
                    _G.log_info(f"Pending job {job.job_name}")
                    self.add_job(job)
                    continue
            unprocessed.append(job)
        self.queued_jobs = unprocessed
        # Pick highest priority pending job
        if self.pending_jobs:
            self.pending_jobs.sort(key=lambda x: x.priority)
            self.execute_job(self.pending_jobs.pop())
            return
        else:
            if (datetime.now() - self.last_idle_time).total_seconds() > self.idle_log_interval:
                self.display_queue()
                self.last_idle_time = datetime.now()

    def execute_job(self, job):
        if not job:
            _G.log_warning("No job to execute!")
            return
        msg = "Pending jobs:\n"
        for j in self.pending_jobs:
            msg += f"{j.job_name} next_run: {j.next_run}\n"
        _G.log_info(msg+'\n---\n')
        _G.log_info(f"Executing job: {job.job_name}")
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
                _G.log_info("Job signaled return")
                job_ret = self.current_job.return_value
                if type(job_ret) != NeoError and job_ret.errno != 0:
                    self.job_returns.append(job_ret)
                return False
        except StopIteration as ret:
            _G.log_info("Job has stopped")
            job_ret = self.current_job.return_value or ret.value
            if type(job_ret) != NeoError and job_ret.errno != 0:
                self.job_returns.append(job_ret)
            return False
        return True

    def queue_job(self, job, queue_next:bool=True):
        if queue_next:
            job.calc_next_run()
        self.queued_jobs.append(job)
        _G.log_info(f"Queued job: {job.job_name}, next run: {job.next_run}")

    def start(self):
        _G.log_info("Job scheduler started")
        self.running = True

    def stop(self, reason:str='manual stop'):
        _G.log_warning(f"Job stopped: {reason}")
        self.running = False
        self.stop_job(queue_next=False)

    def save_status(self):
        _G.log_info("Saving job scheduler status")
        savefile = f"{self.save_path}/.job_scheduler_{self.name}.json"
        with open(savefile, 'w') as f:
            json.dump(self.to_dict(), f)

    def load_status(self, path_dir):
        if self.current_job:
            _G.log_error(f"Unable to load while job is running!")
            return
        filename = f"{path_dir}/.job_scheduler_{self.name}.json"
        _G.log_info(f"Loading job scheduler data from {filename}")
        if not os.path.exists(filename):
            _G.log_warning("Data file not found!")
            return
        with open(filename, 'r') as f:
            data = json.load(f)
            queued_bak = [j for j in self.queued_jobs]
            self.pending_jobs = []
            self.queued_jobs  = []
            data = {**self.to_dict(), **data}
            self.idle_log_interval = data['idle_log_interval']
            self.job_pick_interval = data['job_pick_interval']
            for job_data in data['pending_jobs']:
                job_module = getattr(jobs, job_data['job_name'])
                job_cls  = getattr(job_module, job_data['class'])
                job_instance = job_cls()
                job_instance.load_data(job_data)
                self.pending_jobs.append(job_instance)
            for job_data in data['queued_jobs']:
                job_module = getattr(jobs, job_data['job_name'])
                job_cls  = getattr(job_module, job_data['class'])
                job_instance = job_cls()
                job_instance.load_data(job_data)
                self.queued_jobs.append(job_instance)
        _G.log_info("Data successfully loaded")
        queued_job_names = [j.job_name for j in self.queued_jobs]
        msg = "Queued jobs:\n" + '\n'.join(queued_job_names) + '\n---\n'
        msg += "Expected jobs:\n"
        for j in queued_bak:
            msg += f"[{j.job_name in queued_job_names}] {j.job_name} next_run: {j.next_run}\n"
            if j.job_name not in queued_job_names:
                _G.log_info(f"Re-queuing job: {j.job_name} that not found in loaded data")
                self.queued_jobs.append(j)
        _G.log_info(msg)
        self.display_queue()
        self.last_scan_time = datetime.now() - timedelta(days=1)

    def to_dict(self):
        return {
            'name': self.name,
            'pending_jobs': [job.to_dict() for job in self.pending_jobs],
            'queued_jobs': [job.to_dict() for job in self.queued_jobs],
            'last_idle_time': self.last_idle_time.timestamp(),
            'idle_log_interval': self.idle_log_interval,
            'job_pick_interval': self.job_pick_interval,
        }

    def terminate(self):
        _G.log_info("Terminating job scheduler")
        self.stop('terminated')
        self.save_status()
        try:
            if self.context:
                self.context.close()
            self.playwright.stop()
        except Exception:
            pass

    def display_queue(self):
        msg  = '\n=== Job Queue ===\n'
        msg2 = '\n--- Disabled Jobs ---\n'
        for job in self.queued_jobs:
            ss = f"{job.job_name} next_run: {job.next_run}\n"
            if job.enabled:
                msg += ss
            else:
                msg2 += ss
        msg += msg2
        msg += "\n=================\n"
        _G.log_info(msg)
