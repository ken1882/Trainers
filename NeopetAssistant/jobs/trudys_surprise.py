import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from random import randint
import page_action as action

class TrudysSurpriseJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("trudys_surprise", "https://www.neopets.com/trudys_surprise.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(randint(10, 20)) # inside an iframe, hope it'll load
        canvas = self.page.query_selector("#trudyContainer")
        box = canvas.bounding_box()
        action.scroll_to(self.page, 0, box['y'])
        mx = box['x'] + box['width'] // 2 + randint(-10, 10)
        my = box['y'] + box['height'] * 0.7 + randint(-10, 10)
        yield from _G.rwait(2)
        _G.log_info(f"Clicking at {mx}, {my}")
        self.page.mouse.click(mx, my)
        yield from _G.rwait(20) # let the slots spin
