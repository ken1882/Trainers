import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class DesertedTombJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("deserted_tomb", "https://www.neopets.com/worlds/geraptiku/tomb.phtml", **kwargs)

    def execute(self):
        pass
