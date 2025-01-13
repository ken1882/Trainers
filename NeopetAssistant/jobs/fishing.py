import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class FishingJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("fishing", "https://www.neopets.com/water/fishing.phtml", **kwargs)

    def execute(self):
        pass
