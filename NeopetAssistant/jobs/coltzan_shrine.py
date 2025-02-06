import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class ColtzanShrineJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("coltzan_shrine", "https://www.neopets.com/desert/shrine.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.click_element('input[type=submit]', -1)
        yield
