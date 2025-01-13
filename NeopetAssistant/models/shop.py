import _G
import utils
from datetime import datetime, timedelta
from errors import NeoError

NAME_DICT = {
    1: "fresh_foods",
    2: "magic_shop",
    3: "toy_shop",
    4: "unis_clothing_shop",
    5: "grooming_parlour",
    7: "magical_bookshop",
    8: "collectable_card_shop",
    9: "battle_magic",
    56: "merifoods",
}

class NeoShop:
    def __init__(self, id):
        if id not in NAME_DICT:
            raise NeoError(f"Invalid shop id: {id}")
        self.name = NAME_DICT[id]
        self.url = f"https://www.neopets.com/objects.phtml?type=shop&obj_type={id}"
        self.last_visited = datetime.now() - timedelta(days=1)
        self.next_visit = datetime.now()
        self.min_interval = timedelta(hours=1)
        self.max_interval = timedelta(days=1)
        self.interval = timedelta(hours=1)
        self.enabled = True
