import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class MolatarQuarryJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("moltara_quarry", "https://www.neopets.com/magma/quarry.phtml", **kwargs)

    def execute(self):
        pass
