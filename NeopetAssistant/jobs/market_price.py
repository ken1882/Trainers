import _G
import utils
import re
from random import randint
from copy import copy
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import NeoItem
from models import player
from collections import defaultdict
import jellyneo as jn

class MarketPriceJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("market_price", "https://www.neopets.com/shops/wizard.phtml", **kwargs)
        self.priority = -9999
        self.rate_limited = False

    def load_args(self):
        self.rescan_count = self.args.get('rescan_count', 3)
        self.refresh_interval = self.args.get('refresh_interval', 3)
        self.item_queue = self.args.get('item_queue', [])
        self.scan_batch = self.args.get('scan_batch', 5)
        self.scan_interval = self.args.get('scan_interval', 300)

    def execute(self):
        yield from _G.rwait(2)
        self.collect_items()
        yield from self.scan_all()

    def collect_items(self):
        self.collect_database_items()
        self.collect_stocked_items()
        _G.log_info(f"Total items to scan: {len(self.item_queue)}")

    def collect_stocked_items(self):
        for item_name in player.data.shop_inventory:
            if item_name in self.item_queue:
                continue
            self.item_queue.append(item_name)

    def collect_database_items(self):
        curt = datetime.now().timestamp()
        for item in jn.Database.values():
            if item['rarity'] > 300:
                continue
            if item['name'] in self.item_queue:
                continue
            if curt - item['price_timestamp'] < jn.CACHE_TTL:
                continue
            self.item_queue.append(item['name'])

    def scan_all(self):
        cnt = 0
        while cnt < self.scan_batch:
            if not self.item_queue:
                break
            item_name = self.item_queue.pop(0)
            item = jn.Database.get(item_name.lower(), None)
            if item and datetime.now().timestamp() - item["price_timestamp"] < jn.CACHE_TTL:
                _G.log_info(f"{item_name} is scanned recently at {datetime.fromtimestamp(item['price_timestamp'])}, skip")
                continue
            cnt += 1
            price = yield from self.search_item(item_name)
            if price and price < 10**10:
                jn.update_item_price(item_name, price)

    def search_item(self, item_name, depth=0, lowest=10**10):
        _G.log_info(f"Searching item: {item_name}")
        if self.has_content('too many searches'):
            return
        self.page.query_selector('#shopwizard').fill(item_name)
        yield from _G.rwait(0.5)
        self.click_element('#submit_wizard')
        yield from _G.rwait(2)
        if self.has_content('too many searches'):
            return
        yield from self.wait_until_element_found(lambda _: None, lambda: None, '.wizard-results-text')
        self.rate_limited = False
        while depth < self.rescan_count:
            yield from _G.rwait(2)
            yield from self.wait_until_element_found(lambda _: None, lambda: None, '#resubmitWizard')
            rows = self.page.query_selector_all('.wizard-results-price')
            if rows:
                price = utils.str2int(rows[0].text_content())
                if price < lowest:
                    lowest = price
                    depth = 0
            _G.log_info(f"Lowest price: {lowest} (depth={depth})")
            btn = self.page.query_selector('#resubmitWizard')
            visible = self.scroll_to(node=btn)
            yield from _G.rwait(self.refresh_interval)
            if not visible: # probably a bad idea
                yield from self.goto()
                ret = yield from self.search_item(item_name, depth+1, lowest)
                lowest = min(lowest, ret)
                return lowest
            if btn:
                self.click_element(node=btn)
            else:
                self.click_element('#resubmitWizard')
            depth += 1
        yield from self.goto()
        return lowest

    def calc_next_run(self):
        self.next_run = datetime.now() + timedelta(seconds=self.scan_interval)
        if self.rate_limited:
            self.next_run += timedelta(minutes=30)
        return self.next_run