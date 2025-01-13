from jobs.base_job import BaseJob
from playwright import Playwright

class JobScheduler:
    '''
    This class is suppoed to run in a different thread than main thread.
    '''
    def __init__(self, playwright: Playwright):
        self.pending_jobs = []
        self.queued_jobs = []
        self.running_job = None
        self.playwright = playwright
        self.pw = self.playwright

    def add_job(self, job):
        self.pending_jobs.append(job)

    def update(self):
        if self.running_job:
            return

        if len(self.queued_jobs) == 0:
            self.queued_jobs = self.pending_jobs
            self.pending_jobs = []

        if len(self.queued_jobs) > 0:
            job = self.queued_jobs.pop(0)
            self.execute_job(job)

    def execute_job(self, job):
        self.running_job = job
        job.execute()
        self.running_job = None