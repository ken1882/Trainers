import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from random import randint

class AnchorManagementJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("anchor_management", "https://www.neopets.com/pirates/anchormanagement.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.scroll_to(0, 50)
        yield from _G.rwait(randint(30, 100) / 100.0)
        self.click_element('#btn-fire')
        yield
