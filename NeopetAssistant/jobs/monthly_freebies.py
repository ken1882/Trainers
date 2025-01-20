import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class MonthlyFreebiesJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("monthly_freebies", "https://www.neopets.com/freebies/index.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(5)

    def calc_next_run(self):
        return super().calc_next_run('monthly')
