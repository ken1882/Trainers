import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class NeggCaveJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("negg_cave", "https://www.neopets.com/shenkuu/neggcave/", **kwargs)

    def execute(self):
        pass