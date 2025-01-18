import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class GrumpyKingJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("grumpy_king", "https://www.neopets.com/medieval/grumpyking.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        self.presented = False
        if 'outtolunch.gif' in self.page.content():
            _G.log_info("Grumpy King is unavailable, return after 1 hour")
            return

    def calc_next_run(self):
        if self.presented:
            return super().calc_next_run()
        self.next_run = datetime.now() + timedelta(hours=1)
        return self.next_run
