import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class AppleBobbingJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("apple_bobbing", "https://www.neopets.com/halloween/applebobbing.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.click_element('#bob_button')

