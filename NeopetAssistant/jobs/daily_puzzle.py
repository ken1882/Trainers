import _G
import utils
import re
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action

class DailyPuzzleJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("daily_puzzle", "https://www.jellyneo.net/?go=dailypuzzle", **kwargs)
        self.page_url = "https://www.neopets.com/community/index.phtml"

    def execute(self):
        yield from _G.rwait(2)
        pan = self.page.query_selector('.large-7')
        ss = pan.query_selector_all('strong')
        answer = ss[3].text_content().strip().lower()
        _G.log_info(f"Found Answer: {answer}")
        yield from self.goto(self.page_url)
        yield from _G.rwait(2)
        sel = self.page.query_selector('select[name=trivia_response]')
        self.scroll_to(node=sel)
        opts = sel.query_selector_all('option')
        yield from _G.rwait(1)
        for opt in opts:
            if opt.text_content().strip().lower() == answer:
                sel.select_option(str(opt.get_property('value')))
        yield from _G.rwait(1)
        self.click_element('input[type=submit]', -1)
