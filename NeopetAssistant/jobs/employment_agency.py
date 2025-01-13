import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class EmploymentAgencyJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("employment_agency", "https://www.neopets.com/faerieland/employ/employment.phtml", **kwargs)

    def execute(self):
        pass