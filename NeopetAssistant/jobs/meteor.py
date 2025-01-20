import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class MeteorJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("meteor", "https://www.neopets.com/moon/meteor.phtml", **kwargs)

    def execute(self):
        pass
