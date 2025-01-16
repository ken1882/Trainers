import _G
import captcha
import page_action as action
import re
import utils
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import Transaction, NeoItem
from random import randint

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

    def goto(self, url):
        _G.log_info("Waiting for shop page to load")
        self.page.once("load", self.on_page_load)
        yield
        self.page.goto(url, wait_until='commit')
        while not self.signal.get('load', False):
            yield

    def on_page_load(self):
        _G.log_info("Page loaded")
        self.signal['load'] = True

    def visit(self):
        yield from self.goto(self.url)
        self.last_visited   = datetime.now()
        next_visit_seconds  = randint(self.min_revisist_seconds, self.max_revisist_seconds)
        self.next_visit     = datetime.now() + timedelta(seconds=next_visit_seconds)

    def scan_goods(self):
        if not self.page:
            _G.log_error("Page not loaded")
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
        _G.log_info(f"Buying {good['name']} ({good['price']} NP)")
        bb = good['node'].bounding_box()
        action.scroll_to(self.page, 0, max(bb['y'] - 100, 0))
        action.click_node(self.page, good['node'], y_mul=0.3, random_x=(-20, 20))
        yield from _G.rwait(randint(30, 100) / 100.0)
        confirm = self.page.query_selector('#confirm-link')
        action.click_node(self.page, confirm)
        self.last_captcha_url = None
        result = yield from self.haggle(good_info=good)
        if result:
            _G.log_info(f"Transaction success: {result}")
        else:
            _G.log_info("Failed to purchase item")
        return result

    def reload(self, page=None):
        self.page = page if page else self.page
        if not self.page:
            _G.log_warning("No page assigned")
            return
        page.reload()


    def haggle(self, last_price=0, depth=0, good_info=None):
        if 'SOLD OUT!' in self.page.content():
            _G.log_info("Item is sold out")
            return False
        yield from self.wait_until_captcha_updated()
        purpose_node = self.page.query_selector('#shopkeeper_makes_deal')
        action.scroll_to(self.page, 0, max(0, purpose_node.bounding_box()['y'] - 300))
        max_price = utils.str2int(purpose_node.text_content())
        bargain_price = self.determine_strategy(last_price, max_price, depth)
        inp_node = self.page.query_selector('input[name=current_offer]')
        action.click_node(self.page, inp_node)
        self.page.keyboard.press('Control+A')
        input_str = str(bargain_price)+'E'
        for i,digit in enumerate(input_str):
            if digit == 'E':
                break
            self.page.keyboard.press(digit)
            yield from _G.rwait(self.calc_numkey_interval(input_str[i], input_str[i+1]))
        self.solve_captcha()

        if 'accept' in self.page.content():
            item_name = good_info['name'] if 'name' in good_info else 'Unknown'
            return Transaction(
                [NeoItem(0, 'NP', bargain_price)],
                [NeoItem(item_name, item_name, 1)],
                f"Purchased from Neopian Shop {self.name if self.name else 'Unknown'}",
            ).log()
        yield from self.haggle(bargain_price, depth+1, good_info)

    def determine_strategy(self, last_price, max_price, depth=0):
        if last_price < 3000:
            return self.rounded_up(last_price, max_price, depth)
        raise NeoError(1, f"No strategy defined for price {last_price} {max_price}")

    def rounded_up(self, last_price, max_price, depth):
        if depth > 5:
            return max_price
        if last_price == 0:
            return int(max_price * 0.4 // 10 * 10)
        delta = max_price - last_price
        step  = 20
        if delta > 500:
            step = 100
        elif delta > 100:
            step = 50
        ret = max(1, min(max_price, last_price + int(delta * 0.4 // step * step)))
        if ret == last_price:
            ret = int(max_price // 10 * 10)
        return ret

    def calc_numkey_interval(self, current, next):
        keys = '1234567890..........E'
        delta = abs(keys.index(current) - keys.index(next))
        ret = 0.2
        for _ in range(delta):
            ret += randint(10, 30) / 100.0
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
        while url != self.last_captcha_url:
            yield from _G.wait(1)
            url = captcha.get_captcha_url(self.page)
        self.last_captcha_url = url

