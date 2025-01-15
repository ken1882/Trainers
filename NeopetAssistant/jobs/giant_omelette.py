import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class GiantOmeletteJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("giant_omelette", "https://www.neopets.com/prehistoric/omelette.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.click_element('button[type=submit]', -1)

