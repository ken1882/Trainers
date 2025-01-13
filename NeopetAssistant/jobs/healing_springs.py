import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class HealingSpringsJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("healing_springs", "https://www.neopets.com/faerieland/springs.phtml", **kwargs)

    def execute(self):
        pass
    