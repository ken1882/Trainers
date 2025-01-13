import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class ForgottenShoreJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("forgotten_shore", "https://www.neopets.com/pirates/forgottenshore.phtml", **kwargs)

    def execute(self):
        pass
