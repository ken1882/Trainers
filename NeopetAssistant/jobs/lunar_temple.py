import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class LunarTempleJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("lunar_temple", "https://www.neopets.com/shenkuu/lunar_temple.phtml", **kwargs)

    def execute(self):
        pass
    