import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from random import randint

class FishingJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("fishing", "https://www.neopets.com/water/fishing.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.scroll_to(0, 100)
        yield from _G.rwait(randint(30, 100) / 100.0)
        self.click_element('input[type=submit]', -1)
        yield

    def calc_next_run(self):
        self.next_run = datetime.now() + timedelta(hours=6) + timedelta(minutes=randint(0, 60))
        return self.next_run
