import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class GraveDangerJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("grave_danger", "https://www.neopets.com/halloween/gravedanger.phtml", **kwargs)

    def execute(self):
        pass
    