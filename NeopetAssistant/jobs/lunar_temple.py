import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action

class LunarTempleJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("lunar_temple", "https://www.neopets.com/shenkuu/lunar/", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        for node in self.page.query_selector_all('a[href]'):
            if '?show=puzzle' not in str(node.get_property('href')):
                continue
            node.click()
            break
        yield from _G.rwait(2)
        self.scroll_to(0, 300)
        yield from _G.rwait(1)
        self.run_js('lunar_temple')
        yield from _G.rwait(1)
        self.page.query_selector('#answer').query_selector('input').click()
        yield from _G.rwait(2)
