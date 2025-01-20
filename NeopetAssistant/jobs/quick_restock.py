import _G
import utils
import re
from random import randint
from copy import copy
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import NeoItem
from collections import defaultdict
import jellyneo as jn

class QuickRestockJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("quick_restock", "https://www.neopets.com/quickstock.phtml", **kwargs)
        self.deposite_value = 900000 # 900K
        self.restock_profit = 1000
        self.category_keeps = {
            'food': 5,
            'toy': 1,
            'grooming': 1,
        }

    def execute(self):
        yield from _G.rwait(2)
        yield from self.scan_all_items()
        yield from self.process_actions()

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
                'actions': available_acts,
                'ref': None,
            })
        jn.batch_search([item['name'] for item in self.items], False)
        jn_done = False
        while not jn_done:
            jn_done = jn.FLAG_BUSY
            yield
        for item in self.items:
            item['ref'] = NeoItem(name=item['name'])
            item['ref'].update_jn()
        self.items = sorted(self.items, key=lambda x: x['ref'].value_pc)

    def process_actions(self):
        keeps = copy(self.category_keeps)
        for item in self.items:
            yield
            cat = item['ref'].get_category()
            if item['ref'].is_rubbish():
                pass
            elif item['ref'].value_pc >= self.deposite_value:
                _G.log_info(f"High value item: {item['name']}")
            elif cat in keeps and keeps[cat] > 0:
                keeps[cat] -= 1
                continue
            for act in reversed(item['actions']):
                aname = act.get_attribute('value')
                if aname == 'closet':
                    act.click()
                    break
                elif item['ref'].is_rubbish() and aname == 'donate':
                    act.click()
                    break
                elif aname == 'deposit':
                    act.click()
                    break
        yield from _G.rwait(2)
        self.page.query_selector_all('input[type=submit]')[-1].click()
