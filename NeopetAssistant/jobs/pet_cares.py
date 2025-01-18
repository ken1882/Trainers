import _G
import utils
import re
from random import randint
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import NeoItem
from collections import defaultdict
import jellyneo as jn

FEED_BLACKLIST = [
    r"poison",
    r"rotten",
    r"dung",
    r"glowing",
    r"clay",
    r"smelly",
]

MAX_FEED_VALUE = 1000
MAX_FEED_LEVEL = 8

HUNGER_LEVEL_MAP = defaultdict(lambda: 10, {
    "dying": 0,
    "starving": 1,
    "famished": 2,
    "very hungry": 3,
    "hungry": 4,
    "not hungry": 5,
    "fine": 6,
    "satiated": 7,
    "full up": 8,
    "very full": 9,
    "bloated": 10,
    "very bloated": 11,
})

class PetCaresJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("pet_cares", "https://www.neopets.com/home/", **kwargs)
        self.pets  = []
        self.items = []
        self.selected_pet = None

    def execute(self):
        self.scan_all_pets()

    def scan_all_pets(self):
        self.pets = []
        nodes = self.page.query_selector_all('.hp-carousel-nameplate')
        for node in nodes:
            name = node.get_attribute('data-name')
            if not name:
                continue
            self.pets.append({
                'name': name,
                'health': node.get_attribute('data-health'),
                'max_health': node.get_attribute('data-maxhealth'),
                'hunger': node.get_attribute('data-hunger'),
                'level': node.get_attribute('data-level'),
                'species': node.get_attribute('data-species'),
                'color': node.get_attribute('data-color'),
                'mood': node.get_attribute('data-mood'),
                'active': node.get_attribute('data-active'),
                'node': node
            })
        return self.pets

    def scan_usable_items(self):
        self.items = []
        nodes = self.page.query_selector_all('.petCare-itemgrid-item')
        for node in nodes:
            name = node.get_attribute('data-itemname')
            if not name:
                continue
            self.items.append(NeoItem({
                'name': name,
                'id': node.get_attribute('id'),
                'image': node.get_attribute('data-image'),
                'description': node.get_attribute('data-itemdesc'),
                'rariry': node.get_attribute('data-rarity'),
                'value_npc': node.get_attribute('data-itemvalue'),
                'value_pc': 0,
                'item_type': node.get_attribute('data-itemtype'),
            }))
        return self.items

    def select_pet(self, index):
        if index < 0 or index >= len(self.pets):
            _G.log_warning(f"Invalid pet index: {index} (total pets: {len(self.pets)})")
            return
        self.selected_pet = self.pets[index]
    
    def unselect(self):
        self.selected_pet = None
        self.page.mouse.click(50+randint(-10, 10), 200+randint(-10, 100))

    def customise(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareCustomiseLink')
    
    def read(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkRead')
    
    def feed(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkFeed')
        node.click()
        yield from _G.rwait(5)
        self.scan_usable_items()
        item_index = yield from self.determine_feed_item()
    
    def determind_item_to_feed(self):
        yield
        if not self.items:
            return
        candiates = []
        for item in self.items:
            if item.is_rubbish():
                continue
            if any(re.search(pattern, item.name, re.I) for pattern in FEED_BLACKLIST):
                continue
            candiates.append(item)
        # update jellyneo data
        jn.batch_search([item.name for item in candiates], False)
        jn_done = False
        while not jn_done:
            jn_done = jn.FLAG_BUSY
            yield
        [item.update_jn() for item in candiates]
        candiates = [item for item in candiates if "disease" not in item.effects]
        for i, item in enumerate(sorted(candiates, key=lambda x: x.value_pc)):
            if item.value_pc < MAX_FEED_VALUE:
                return i
        return -1

    def play(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkPlay')
    
    def groom(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkGroom')
    
    def heal(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkHeal')
    
    def determine_feed_item(self):
        pass