import _G
import captcha
import page_action as action
import re
import utils
import importlib
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import Transaction, NeoItem
from models.mixins.base_page import BasePage

NAME_DESC_DICT = {
    'purchase_item': ['purchase item(s) from any neopian shop', 'purchase item'],
    'spin_wheel': ['spin the wheel'],
    'play_game': ['play any game'],
    'groom_pet': ['groom one of your neopet'],
}

class BaseQuest(BasePage):
    def __init__(self, **kwargs):
        page = kwargs.get('page', None)
        url  = kwargs.get('url', 'https://neopets.com/questlog/')
        super().__init__(page, url)

    def solve(self):
        yield

def get_quest_class_by_desc(desc):
    for name, desc_list in NAME_DESC_DICT.items():
        if any([d in desc for d in desc_list]):
            module = importlib.import_module(f'quests.{name}')
            return getattr(module, utils.snake2pascal(name))
    return None
