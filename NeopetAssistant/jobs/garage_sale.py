import _G
import utils
import re
from random import randint
from jobs.base_job import BaseJob
from models import shop
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action

class GarageSaleJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("garage_sale", "https://www.neopets.com/winter/igloo.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(1)
        self.page.query_selector('a[href*="igloo2.phtml"]').click()
        yield from _G.rwait(2)
        yield from self.scan_all_items()
        yield from self.process_actions()

    def scan_all_items(self):
        self.items = []
        container = self.page.query_selector('#items_for_sale')
        nodes = container.query_selector_all('table > tbody > tr > td')
