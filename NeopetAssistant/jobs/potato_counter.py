import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError


class PotatoCounterJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("potato_counter", "https://www.neopets.com/medieval/potatocounter.phtml", **kwargs)

    def execute(self):
        times = 3
        while times > 0:
            yield from _G.rwait(2)
            self.run_js('potato')
            yield from _G.rwait(5)
            ans = 999
            try:
                ans = utils.str2int(self.page.query_selector('#potato-counter-overlay').text_content())
            except Exception:
                pass
            if ans > 99:
                _G.log_warning(f"Invalid potato count: {ans}, probably cheat detection")
            else:
                field = self.page.query_selector('#content').query_selector('center > form')
                field.query_selector('input[type=text]').fill(str(ans))
                yield from _G.rwait(1)
                field.query_selector('input[type=submit]').click()
                times -= 1
            yield from self.goto()
