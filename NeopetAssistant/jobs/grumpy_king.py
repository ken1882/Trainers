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
        self.scroll_to(0, 250)
        self.run_js('king_autofill')
        yield from _G.rwait(1)
        self.click_element('button[type=submit]', -1)
        self.presented = True

    def calc_next_run(self):
        if self.presented:
            return super().calc_next_run()
        self.next_run = datetime.now() + timedelta(hours=1)
        return self.next_run
