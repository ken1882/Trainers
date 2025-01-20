import _G
import utils
import re
import json
import jellyneo as jn
from datetime import datetime, timedelta

TRANSACTION_HISTORY_DIR = 'transaction_history'

TRASH_NAME_REGEXES = [
    r"dung"
]
class NeoItem:
    def __init__(self, **kwargs):
        self.id       = kwargs.get('id', None)
        self.name     = kwargs.get('name', 'Unknown Item')
        self.image    = kwargs.get('image', '')
        self.quantity = kwargs.get('quantity', 1)
        self.value_npc = kwargs.get('value_npc', 10) # in-game data, mostly unaccurate
        self.value_pc  = kwargs.get('value_pc', 10) # price from jellyneo
        self.description = kwargs.get('description', '')
        self.rarity = kwargs.get('rarity', 10)
        self.item_type = kwargs.get('item_type', 'food')
        self.effects = []

    def __str__(self):
        return f"<NeoItem: {self.to_dict()}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "image": self.image,
            "value_npc": self.value_npc,
            "value_pc": self.value_pc,
            "description": self.description,
            "rarity": self.rarity,
            "item_type": self.item_type
        }

    def update_jn(self):
        '''
        Update item data from jellyneo
        '''
        data = jn.get_item_details_by_name(self.name)
        if not data:
            return self
        self.id = data.get('id', self.id)
        self.image = data.get('image', self.image)
        self.value_pc = data.get('price', self.value_pc)
        self.description = data.get('description', self.description)
        self.rarity = data.get('rarity', self.rarity)
        self.item_type = data.get('category', self.item_type)
        self.effects = data.get('effects', self.effects)
        return self

    def get_category(self):
        if 'food' in self.item_type.lower() or 'edible' in self.effects:
            return 'food'
        if 'playable' in self.effects:
            return 'toy'
        if self.item_type.lower() == 'grooming':
            return 'grooming'
        return 'other'

    def is_rubbish(self):
        if any(re.search(regex, self.name, re.I) for regex in TRASH_NAME_REGEXES):
            return True
        if 'diseases' in self.effects:
            return True
        return False

class Transaction:
    def __init__(self, spents:list[NeoItem], gains:list[NeoItem], message:str, timestamp=None, **kwargs):
        self.items_spent  = spents
        self.items_gained = gains
        self.message      = message
        self.timestamp    = timestamp or datetime.now()
        self.kwargs       = kwargs

    def log(self, disable_json_output=False):
        log_str = f"Transaction Log: {self.timestamp}\n"
        log_str += f"Message: {self.message}\n"
        log_str += f"Items Spent: {'None' if not self.items_spent else ''}\n"
        for item in self.items_spent:
            log_str += f"\t{item.name} x{item.quantity}\n"
        log_str += f"Items Gained: {'None' if not self.items_gained else ''}\n"
        for item in self.items_gained:
            log_str += f"\t{item.name} x{item.quantity}\n"
        _G.log_info(log_str)
        if not disable_json_output:
            filename = f"{TRANSACTION_HISTORY_DIR}/{self.timestamp.strftime('%Y-%m-%d')}.json"
            with open(filename, 'a') as f:
                f.write(json.dumps(self.to_dict()))
                f.write('\n')
        return self

    def __str__(self):
        return f"<Transaction: {self.to_dict()}>"

    def to_dict(self):
        return {
            "timestamp": self.timestamp.timestamp(),
            "message": self.message,
            "items_spent": [item.to_dict() for item in self.items_spent],
            "items_gained": [item.to_dict() for item in self.items_gained],
            **self.kwargs
        }