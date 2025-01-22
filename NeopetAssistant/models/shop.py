import _G
import captcha
import page_action as action
import re
import utils
import math
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import Transaction, NeoItem
from models.mixins.base_page import BasePage
from random import randint
import jellyneo as jn

NAME_DICT = {
    1: "fresh_foods",
    2: "magic_shop",
    3: "toy_shop",
    4: "unis_clothing_shop",
    5: "grooming_parlour",
    7: "magical_bookshop",
    8: "collectable_card_shop",
    9: "battle_magic",
    14: "chocolate_factory",
    15: "the_bakery",
    16: "smoothie_shop",
    34: "coffee_cave",
    35: "slushie_shop",
    39: "faerie_foods",
    46: "huberts_hotdogs",
    56: "merifoods",
}

class NeoShop(BasePage):
    def __init__(self, id, **kwargs):
        if id not in NAME_DICT:
            raise NeoError(f"Invalid shop id: {id}")
        self.name = NAME_DICT[id]
        url = f"https://www.neopets.com/objects.phtml?type=shop&obj_type={id}"
        page = kwargs.get('page', None)
        super().__init__(page, url)
        self.last_visited = datetime.now() - timedelta(days=1)
        self.next_visit = datetime.now()
        self.goods = []
        self.currency = kwargs.get('currency', 'np')
        self.min_revisist_seconds = kwargs.get('min_revisist_seconds', 60*30)
        self.max_revisist_seconds = kwargs.get('max_revisist_seconds', 60*90)
        self.limit_reset_type = kwargs.get('limit_reset_type', 'daily')
        self.limit_reset_seconds = kwargs.get('limit_reset_seconds', 60*60*4)
        self.purchase_limit = kwargs.get('purchase_limit', 0)
        self.transaction_history = []

    def visit(self):
        yield from self.goto()
        self.last_visited   = datetime.now()
        next_visit_seconds  = randint(self.min_revisist_seconds, self.max_revisist_seconds)
        self.next_visit     = datetime.now() + timedelta(seconds=next_visit_seconds)

    def scan_goods(self):
        if not self.page:
            _G.log_error("Page not loaded")
            return
        nodes = self.page.query_selector_all(".shop-item")
        self.goods = []
        for i, node in enumerate(nodes):
            stock, price = node.query_selector_all('.item-stock')
            self.goods.append({
                'index': i,
                'name': node.query_selector('.item-name').text_content(),
                'stock': utils.str2int(stock.text_content().split()[0]),
                'price': utils.str2int(price.text_content().split()[1]),
                'ref': None,
                'node': node,
                'profit': 0,
            })

    def lookup_goods_details(self):
        goods_names = [good['name'] for good in self.goods]
        jn.batch_search(goods_names, False)
        jn_done = False
        while not jn_done:
            jn_done = not jn.FLAG_BUSY
            yield
        for good in self.goods:
            good['ref'] = jn.get_item_details_by_name(good['name'])

    def is_purchase_limited(self):
        if not self.purchase_limit:
            return False
        curt = datetime.now()
        latest_purchase_time = self.transaction_history[-1].timestamp
        if self.limit_reset_type == 'daily':
            return latest_purchase_time.month == curt.month and latest_purchase_time.day == curt.day
        # check cooldown
        return (curt - latest_purchase_time).total_seconds() < self.limit_reset_seconds

    def get_profitable_goods(self):
        ret = []
        for good in self.goods:
            try:
                profit = good['ref']['price'] - good['price']
            except Exception:
                profit = 0
            if profit > 0:
                good['profit'] = profit
                ret.append(good)
        return sorted(ret, key=lambda x: x['profit'], reverse=True)

    def is_good_buyable(self, good=None, index=None):
        if self.is_purchase_limited():
            return False
        if index:
            good = self.goods[index]
        if self.currency == 'np':
            return good['price'] < action.get_availabe_np(self.page) - _G.ARGV.get('reserve_np', 0)
        NeoError(1, f"Unsupported currency: {self.currency}").raise_exception()
        return False

    def buy_good(self, good=None, index=None, immediate=False):
        if index:
            good = self.goods[index]
        _G.log_info(f"Buying {good['name']} ({good['price']} NP)")
        bb = good['node'].bounding_box()
        action.scroll_to(self.page, 0, max(bb['y'] - 100, 0))
        yield from _G.rwait(0.1)
        action.click_node(self.page, good['node'], y_mul=0.3, random_x=(-20, 20))
        yield from _G.rwait(randint(30, 100) / 100.0)
        confirm = self.page.query_selector('#confirm-link')
        action.click_node(self.page, confirm)
        self.last_captcha_url = None
        last_tlen = len(self.transaction_history)
        yield from self.haggle(good_info=good, immediate=immediate)
        if last_tlen < len(self.transaction_history):
            ret = self.transaction_history[-1]
            _G.log_info(f"Transaction success: {ret}")
            return ret
        else:
            _G.log_info("Failed to purchase item")
            return False

    def reload(self, page=None):
        self.page = page if page else self.page
        if not self.page:
            _G.log_warning("No page assigned")
            return
        page.reload()


    def haggle(self, last_price=0, depth=0, last_max=10**8, good_info=None, immediate=False):
        yield from _G.rwait(1.5)
        if self.has_content('SOLD OUT'):
            _G.log_info("Item is sold out")
            return False
        _G.log_info(f"Haggling with {self.name}")
        yield from self.wait_until_captcha_updated()
        if self.has_content('accept your offer'):
            return self.finalize_haggle(max_price, good_info)
        elif self.has_content('SOLD OUT'):
            _G.log_info("Item is sold out")
            return False
        purpose_node = self.page.query_selector('#shopkeeper_makes_deal')
        action.scroll_to(self.page, 0, max(0, purpose_node.bounding_box()['y'] - 300))
        text = purpose_node.text_content().strip()
        max_price = utils.str2int(text)
        if max_price > last_max:
            max_price = utils.str2int(' '.join(text.split()[-5:]))
            if not max_price:
                max_price = utils.str2int(' '.join(text.split()[-8:]))
        bargain_price = max_price
        _G.log_info(f"Last price: {last_price}, Max price: {max_price}, Depth: {depth}")
        if not immediate and max_price < last_max:
            bargain_price = self.determine_strategy(last_price, max_price, depth)
        _G.log_info(f"Making deal with {bargain_price} NP")
        yield from self.input_number('input[name=current_offer]', bargain_price)
        self.solve_captcha()
        yield from _G.rwait(2)
        while True:
            yield from _G.rwait(0.1)
            try:
                if self.has_content('accept your offer'):
                    return self.finalize_haggle(bargain_price, good_info)
                elif self.has_content('SOLD OUT'):
                    _G.log_info("Item is sold out")
                    return False
                else:
                    break
            except Exception as e:
                pass
        yield from self.haggle(bargain_price, depth+1, max_price, good_info)

    def finalize_haggle(self, price, good_info):
        item_name = good_info['name'] if 'name' in good_info else 'Unknown'
        log = Transaction(
            [NeoItem(name='NP', quantity=price)],
            [NeoItem(name=item_name)],
            f"Purchased from Neopian Shop {self.name if self.name else 'Unknown'}",
        )
        log.update_jn()
        self.transaction_history.append(log)
        return log

    def determine_strategy(self, last_price, max_price, depth=0):
        if max_price > 100000: # usually very rare items
            return max_price
        if last_price < 10000:
            return self.rounded_up(last_price, max_price, depth)
        raise NeoError(1, f"No strategy defined for price {last_price} {max_price}")

    def rounded_up(self, last_price, max_price, depth):
        if depth > 5:
            return max_price
        if last_price == 0:
            return int(max_price * 0.4 // 10 * 10)
        delta = max_price - last_price
        step  = 20
        if delta > 3000:
            step = 1000
        elif delta > 1500:
            step = 500
        elif delta > 300:
            step = 100
        elif delta > 150:
            step = 50
        ret = max(1, min(max_price, last_price + int(delta * 0.4 // step * step)))
        if ret == last_price:
            ret = int(max_price // 10 * 10)
        return ret

    def calc_numkey_interval(self, current, next):
        keys = '1234567890..........E'
        delta = abs(keys.index(current) - keys.index(next))
        ret = 0.1
        for _ in range(delta):
            ret += randint(20, 50) / 1000.0
        return ret

    def solve_captcha(self):
        pos = captcha.solve(self.page)
        if not pos:
            raise NeoError(1, "Failed to solve captcha")
        captcha_canvas = self.page.query_selector('input[type="image"][src*="/captcha_show.phtml"]')
        bb = captcha_canvas.bounding_box()
        mx, my = pos
        mx += bb['x']
        my += bb['y']
        _G.log_info(f"Clicking captcha at {mx}, {my}")
        self.page.mouse.click(mx, my)

    def wait_until_captcha_updated(self):
        url = '_'
        while url == self.last_captcha_url:
            yield from _G.rwait(0.1)
            url = captcha.get_captcha_url(self.page)
        yield from _G.rwait(1)
        self.last_captcha_url = url
