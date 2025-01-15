import _G
import utils
import re
from random import randint
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action

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
    def __init__(self, id, **kwargs):
        if id not in NAME_DICT:
            raise NeoError(f"Invalid shop id: {id}")
        self.name = NAME_DICT[id]
        self.url = f"https://www.neopets.com/objects.phtml?type=shop&obj_type={id}"
        self.last_visited = datetime.now() - timedelta(days=1)
        self.next_visit = datetime.now()
        self.page = None
        self.goods = []
        self.currency = kwargs.get('currency', 'np')
        self.min_revisist_seconds = kwargs.get('min_revisist_seconds', 60*30)
        self.max_revisist_seconds = kwargs.get('max_revisist_seconds', 60*90)
        self.limit_reset_type = kwargs.get('limit_reset_type', 'daily')
        self.limit_reset_seconds = kwargs.get('limit_reset_seconds', 60*60*4)
        self.purchase_limit = kwargs.get('purchase_limit', 0)
        self.transaction_history = []

    def visit(self):
        self.page.goto(self.url)
        self.last_visited   = datetime.now()
        self.next_visit     = datetime.now() + timedelta(seconds=next_visit_seconds)
        next_visit_seconds  = randint(self.min_revisist_seconds, self.max_revisist_seconds)

    def scan_goods(self):
        if not self.page:
            _G.logger.error("Page not loaded")
            return
        nodes = self.page.query_selector_all(".shop-item")
        self.goods = []
        for node in nodes:
            stock, price = node.query_selector_all('.item-stock')
            self.goods.append({
                'name': node.query_selector('.item-name').text_content(),
                'stock': utils.str2int(stock.text_content().split()[0]),
                'price': utils.str2int(price.text_content().split()[1]),
                'node': node
            })

    def is_purchase_limited(self):
        if not self.purchase_limit:
            return False
        curt = datetime.now()
        latest_purchase_time = self.transaction_history[-1].timestamp
        if self.limit_reset_type == 'daily':
            return latest_purchase_time.month == curt.month and latest_purchase_time.day == curt.day
        # check cooldown
        return (curt - latest_purchase_time).total_seconds() < self.limit_reset_seconds

    def is_good_buyable(self, good=None, index=None):
        if self.is_purchase_limited():
            return False
        if index:
            good = self.goods[index]
        if self.currency == 'np':
            return good['price'] < action.get_availabe_np(self.page) - _G.ARGV.get('reserve_np', 0)
        NeoError(1, f"Unsupported currency: {self.currency}").raise_exception()
        return False

    def buy_good(self, good=None, index=None):
        if index:
            good = self.goods[index]
        bb = good['node'].bounding_box()
        action.scroll_to(self.page, 0, bb['y'])
        action.click_node(self.page, good['node'], y_mul=0.3, random_x=(-20, 20), wait=randint(30, 100) / 100.0)
        confirm = self.page.query_selector('#confirm-link')
        action.click_node(self.page, confirm)

    def reload(self, page=None):
        self.page = page if page else self.page
        if not self.page:
            _G.logger.warning("No page assigned")
            return
        page.reload()

