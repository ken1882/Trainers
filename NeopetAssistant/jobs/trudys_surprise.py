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
        canvas = self.page.query_selector("#trudyContainer")
        box = canvas.bounding_box()
        action.scrollTo(self.page, 0, box['y'])
        mx = box['x'] + box['width'] // 2 + randint(-10, 10)
        my = box['y'] + box['height'] * 0.7 + randint(-10, 10)
        self.page.mouse.click(mx, my)
        self.wait_until_element_found(lambda: None, lambda: None, ['#trudyPrizeTitle'], 60)
