import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class DesertedTombJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("deserted_tomb", "https://www.neopets.com/worlds/geraptiku/tomb.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.scroll_to(0, 100)
        self.click_element('input[type=submit]', 1)
        yield from _G.rwait(5)
        self.scroll_to(0, 100)
        self.click_element('input[type=submit]', 1)
        yield from _G.rwait(2)
