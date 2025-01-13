import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class WiseKingJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("wise_king", "https://www.neopets.com/medieval/wiseking.phtml", **kwargs)

    def execute(self):
        pass
