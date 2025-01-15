import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class GiantJellyJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("giant_jelly", "https://www.neopets.com/jelly/jelly.phtml", **kwargs)

    def execute(self):
        node = self.page.query_selector_all('input[type=submit]')[-1]
        node.click()


