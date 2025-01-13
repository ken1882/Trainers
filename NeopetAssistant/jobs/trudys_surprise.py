import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class TrudysSurpriseJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("trudys_surprise", "https://www.neopets.com/trudys_surprise.phtml", **kwargs)

    def execute(self):
        pass