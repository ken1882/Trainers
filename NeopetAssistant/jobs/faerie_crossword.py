import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class FaerieCrosswordJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("faerie_crossword", "https://www.neopets.com/games/crossword/index.phtml", **kwargs)
        self.priority = 10

    def execute(self):
        yield from _G.rwait(2)
        self.click_element('input[type=submit]', 1)
        yield from _G.rwait(2)
        cur_idx = 0
        total_lines = 12
        while cur_idx < total_lines:
            yield from _G.rwait(2)
            self.scroll_to(0, 200)
            table = None
            while not table:
                table = self.page.query_selector('#content')
                yield from _G.rwait(1)
            lines = table.query_selector_all('center > table > tbody > tr > td > a')
            total_lines = len(lines)
            self.run_js('crossword')
            yield from _G.rwait(1)
            lines[cur_idx].click()
            yield from _G.rwait(0.5)
            btn = table.query_selector('center > table > tbody > tr > td > form > input[type=submit]')
            btn.click()
            cur_idx += 1

    def calc_next_run(self):
        return super().calc_next_run('daily')