import _G
import utils
import re
from random import randint
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import NeoItem
from collections import defaultdict
from pprint import pformat
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
MAX_FEED_LEVEL = 8 # full up

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
        pets_num = len(self.pets)
        for i in range(pets_num):
            _G.log_info(f"Careing {self.pets[i]['name']}")
            self.select_pet(i)
            yield from _G.rwait(1)
            while self.is_hungry():
                yield from _G.rwait(1)
                yield from self.feed()
                yield from _G.rwait(1)
                self.select_pet(i)
            yield from _G.rwait(1)
            yield from self.play()
            yield from _G.rwait(1)
            self.select_pet(i)
            yield from _G.rwait(1)
            yield from self.groom()
            yield from _G.rwait(1)
        _G.log_info("Customising")
        self.select_pet(0)
        yield from self.customise()


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
        msg = f"Found {len(self.pets)} pets:"
        msg += "\n" + pformat(self.pets)
        _G.log_info(msg)
        return self.pets

    def scan_usable_items(self):
        self.items = []
        nodes = self.page.query_selector_all('.petCare-itemgrid-item')
        item_names = set()
        for node in nodes:
            name = node.get_attribute('data-itemname')
            if not name:
                continue
            item_names.add(name)
            item = NeoItem(
                name=name,
                id=node.get_attribute('id'),
                image=node.get_attribute('data-image'),
                description=node.get_attribute('data-itemdesc'),
                rariry=node.get_attribute('data-rarity'),
                value_npc=node.get_attribute('data-itemvalue'),
                value_pc=0,
                item_type=node.get_attribute('data-itemtype'),
            )
            item.node = node
            self.items.append(item)
        jn.batch_search(item_names, False)
        jn_done = False
        while not jn_done:
            jn_done = not jn.is_busy()
            yield
        for item in self.items:
            item.update_jn()
        return self.items

    def select_pet(self, index):
        if index < 0 or index >= len(self.pets):
            _G.log_warning(f"Invalid pet index: {index} (total pets: {len(self.pets)})")
            return
        if self.selected_pet:
            self.unselect()
        self.selected_pet = self.pets[index]
        self.pets[index]['node'].click()

    def unselect(self):
        self.selected_pet = None
        self.page.mouse.click(50+randint(-10, 10), 200+randint(-10, 100))

    def use_item(self, index):
        try:
            _G.log_info(f"Using item: {self.items[index].name}")
            self.items[index].node.click()
        except IndexError:
            _G.log_error(f"Invalid item index: {index} (total items: {len(self.items)})")
            return
        yield from _G.rwait(0.5)
        self.page.query_selector('#petCareUseItem').click()
        yield from _G.rwait(2)

    def customise(self):
        '''
        For daily mission, basically take off a thing and wear it back
        '''
        if not self.selected_pet:
            return
        self.page.query_selector('#petCareCustomiseLink').click()
        yield from _G.rwait(10)
        switch = self.page.query_selector('.npcma-slider')
        switch.click()
        yield from _G.rwait(2)
        container = self.page.query_selector('#npcma_AppliedpetItems')
        item_name = container.query_selector('div > span').text_content()
        if not item_name:
            raise NeoError(1, "Please wear at least one item")
        container.query_selector('.npcma-icon-close').click()
        yield from _G.rwait(1)
        self.page.query_selector('.npcma-icon-save-snap').click()
        yield from _G.rwait(5)
        self.page.query_selector('.npcma-ok_button').click()
        yield from _G.rwait(0.5)
        switch.click()
        yield from _G.rwait(3)
        self.page.query_selector('.header-input').fill(item_name)
        yield from _G.rwait(1)
        la = self.page.locator('.ddcontainer')
        lb = self.page.locator('#npcma_customMainContent')
        self.drag_to(la, lb)
        yield from _G.rwait(2)
        self.page.query_selector('.npcma-icon-save-snap').click()
        yield from _G.rwait(3)

    def read(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkRead')

    def feed(self):
        self.page.query_selector('#petCareLinkFeed').click()
        yield from _G.rwait(10)
        yield from self.scan_usable_items()
        item_index = self.determine_item_to_feed()
        yield from self.use_item(item_index)
        self.update_hunger()
        yield from _G.rwait(1)

    def update_hunger(self):
        line = self.page.query_selector('#petCareResult').query_selector_all('div > p')[-1].text_content().lower()
        for word in reversed(HUNGER_LEVEL_MAP.keys()):
            if word in line:
                _G.log_info(f"Pet hunger: {word}")
                self.selected_pet['hunger'] = word
                break

    def determine_item_to_feed(self):
        if not self.items:
            return
        candidates = []
        for item in self.items:
            if item.is_rubbish():
                continue
            if any(re.search(pattern, item.name, re.I) for pattern in FEED_BLACKLIST):
                continue
            candidates.append(item)
        for item in sorted(candidates, key=lambda x: x.value_pc):
            if item.value_pc < MAX_FEED_VALUE:
                return self.items.index(item)
        return -1

    def play(self):
        if not self.selected_pet:
            return
        self.page.query_selector('#petCareLinkPlay').click()
        yield from _G.rwait(10)
        yield from self.scan_usable_items()
        yield from self.use_item(0)

    def groom(self):
        if not self.selected_pet:
            return
        self.page.query_selector('#petCareLinkGroom').click()
        yield from _G.rwait(10)
        yield from self.scan_usable_items()
        yield from self.use_item(0)

    def heal(self):
        if not self.selected_pet:
            return
        node = self.page.query_selector('#petCareLinkHeal')

    def is_hungry(self):
        if not self.selected_pet:
            return False
        return HUNGER_LEVEL_MAP[self.selected_pet['hunger']] < MAX_FEED_LEVEL