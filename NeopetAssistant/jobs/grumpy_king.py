import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class GrumpyKingJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("grumpy_king", "https://www.neopets.com/medieval/grumpyking.phtml", **kwargs)

    def execute(self):
        pass
