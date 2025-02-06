import _G
import utils
import re
from random import randint
from jobs.base_job import BaseJob
from models import shop
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import NeoItem
import page_action as action
import jellyneo as jn

class GarageSaleJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("garage_sale", "https://www.neopets.com/winter/igloo.phtml", **kwargs)
        self.purchase_limit = 10
        self.purchase_times = 0
        self.last_purchase = datetime.now() - timedelta(days=1)

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
        jn.batch_search(list(set([item['name'] for item in self.items])), False)
        jn_done = False
        while not jn_done:
            jn_done = not jn.is_busy()
            yield
        for item in self.items:
            item['ref'] = NeoItem(name=item['name'])
            item['ref'].update_jn()

    def calc_next_run(self):
        if self.purchase_times >= self.purchase_limit:
            return super().calc_next_run()
        curt = datetime.now()
        delta_sec= 300 + randint(10, 300)
        if curt - self.last_purchase < timedelta(seconds=300):
            delta_sec += 300
        self.next_run = curt + timedelta(seconds=delta_sec)
        return self.next_run
