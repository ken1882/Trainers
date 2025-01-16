import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from random import randint

class HealingSpringsJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("healing_springs", "https://www.neopets.com/faerieland/springs.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.scroll_to(0, 100)
        yield from _G.rwait(randint(30, 100) / 100.0)
        self.click_element('input[type=submit]', -1)
        yield
