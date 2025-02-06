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

class QuickRestockJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("quick_restock", "https://www.neopets.com/quickstock.phtml", **kwargs)
        self.priority = -1

    def load_args(self):
        self.deposite_value = self.args.get('deposite_value', 90000)
        self.restock_profit = self.args.get('restock_profit', 1000)
        self.high_value_threshold = self.args.get('high_value_threshold', 10000)
        self.marketprice_adds_rate = self.args.get('marketprice_adds_rate', 0.01)
        self.high_value_adds_rate  = self.args.get('high_value_adds_rate', 0.03)
        self.category_keeps = self.args.get('category_keeps', {"food": 5, "grooming": 1, "toy": 1})
        if type(self.category_keeps) == str:
            string = self.category_keeps
            self.category_keeps = {}
            for pair in string.split(','):
                k, v = pair.split(':')
                self.category_keeps[k.strip()] = int(v)
        self.deposite_blacklist = self.args.get('deposite_blacklist', [])
        if type(self.deposite_blacklist) == str:
            self.deposite_blacklist = [s.lower() for s in self.deposite_blacklist.split(',')]
        self.deposite_whitelist = self.args.get('deposite_whitelist', [])
        if type(self.deposite_whitelist) == str:
            self.deposite_whitelist = [s.lower() for s in self.deposite_whitelist.split(',')]

    def execute(self):
        yield from _G.rwait(2)
        self._stocked = False
        yield from self.scan_all_items()
        yield from self.process_actions()
        if self._stocked:
            yield from self.process_restock()

    def scan_all_items(self):
        self.items = []
        nodes = self.page.query_selector_all('form > table > tbody > tr')
        for node in nodes[:-1]:
            available_acts = node.query_selector_all('input')
            if not available_acts:
                continue
            name = node.query_selector('td').text_content()
            if name.lower() == "check all":
                break
            self.items.append({
                'name': name,
                'ref': None,
                'node': node,
                'act': 'keep',
            })
        jn.batch_search(list(set([item['name'] for item in self.items])), False)
        jn_done = False
        while not jn_done:
            jn_done = not jn.is_busy()
            yield
        for item in self.items:
            item['ref'] = NeoItem(name=item['name'])
            item['ref'].update_jn()

    def process_actions(self):
        keeps = copy(self.category_keeps)
        val_items = sorted(self.items, key=lambda x: x['ref'].value_pc)
        for item in val_items:
            yield
            act_name = 'deposit'
            available_acts = [act.get_attribute('value') for act in item['node'].query_selector_all('input')]
            cat = item['ref'].get_category()
            _G.log_info(f"{item['name']} G:{item['ref'].value_pc - item['ref'].value_npc}")
            if any(re.search(regex, item['name'], re.I) for regex in self.deposite_whitelist):
                pass
            elif item['ref'].rarity == 500:
                _G.log_info(f"Cash item: {item['name']}")
                act_name = 'keep'
            if any(re.search(regex, item['name'], re.I) for regex in self.deposite_blacklist):
                act_name = 'keep'
            elif item['ref'].rarity == 200:
                _G.log_info(f"Artifact: {item['name']}")
            elif item['ref'].value_pc >= self.deposite_value:
                _G.log_info(f"High value item: {item['name']}")
            elif item['ref'].is_rubbish():
                _G.log_info(f"Trash item: {item['name']}")
                act_name = 'donate'
            elif cat in keeps:
                if keeps[cat] > 0:
                    act_name = 'keep'
                if act_name == 'keep':
                    keeps[cat] -= 1
            elif item['ref'].value_pc - item['ref'].value_npc >= self.restock_profit:
                _G.log_info(f"Profitable item: {item['name']}")
                act_name = 'stock'
                self._stocked = True
            elif 'closet' in available_acts:
                act_name = 'closet'

            item['act'] = act_name
        row_height = 24
        viewport_height = 400
        viewport_y = 0
        cur_y = 100
        random_x = (0, 0)
        random_y = (0, 0)
        for item in self.items:
            acts = item['node'].query_selector_all('input')
            for act in reversed(acts):
                aname = act.get_attribute('value')
                if aname == item['act']:
                    _G.log_info(f"Processing {item['name']} with action {aname}")
                    self.click_element(node=act, random_x=random_x, random_y=random_y)
                    yield from _G.rwait(0.2)
                    break
            cur_y += row_height
            if cur_y > viewport_y + viewport_height:
                viewport_y = cur_y
                self.scroll_to(0, viewport_y)
                yield from _G.rwait(1)
        yield from _G.rwait(2)
        btn = self.page.query_selector_all('input[type=submit]')[1]
        yield from _G.rwait(1)
        self.page.on("dialog", lambda dialog: dialog.accept())
        self.click_element(node=btn)
        yield from _G.rwait(3)

    def process_restock(self):
        yield from self.goto("https://www.neopets.com/market.phtml?type=your")
        yield from _G.rwait(2)
        player.data.shop_inventory = {}
        while True:
            rows = self.page.query_selector_all('form[action] > table > tbody > tr')
            goods = rows[1:-1]
            for good in goods:
                self.scroll_to(node=good)
                # yield from _G.rwait(0.5)
                cells = good.query_selector_all('td')
                name = cells[0].text_content().strip()
                amount = utils.str2int(cells[2].text_content().strip())
                market_price = jn.get_item_details_by_name(name).get('price', 0)
                adds = int(market_price * self.marketprice_adds_rate)
                if market_price >= self.high_value_threshold:
                    adds = int(market_price * self.high_value_adds_rate)
                price = int(market_price + adds)
                _G.log_info(f"Setting price for {name} to {price} ({market_price} + {adds})")
                player.data.shop_inventory[name] = {
                    'name': name,
                    'amount': amount,
                    'price': price,
                }
                old_price = utils.str2int(cells[4].text_content().strip())
                if market_price <= 0 or old_price == price:
                    continue
                cells[4].query_selector('input').fill(str(price))
                yield from _G.rwait(0.2)
            yield from _G.rwait(1)
            rows[-1].query_selector('input[type=submit]').click()
            yield from self.wait_until_page_load()
            yield from _G.rwait(1)
            btn = self.page.query_selector('input[name=subbynext]')
            _G.log_info(f"Next page: {btn}")
            if not btn:
                break
            disabled = btn.get_property('disabled').json_value()
            _G.log_info(f"Last page: {disabled}")
            if disabled:
                break
            self.scroll_to(node=btn)
            yield from _G.rwait(0.5)
            btn.click()
            yield from _G.rwait(3)
