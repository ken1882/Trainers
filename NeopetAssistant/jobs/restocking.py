import _G
import utils
import re
from random import randint, shuffle
from jobs.base_job import BaseJob
from models import shop
from datetime import datetime, timedelta
from errors import NeoError
from models import player
import page_action as action

class RestockingJob(BaseJob):
    '''
    kwargs:
    - `candidate_shops:list=[]` list of shop ids to visit
    - `shop_refreshes:int=3` number of times/refreshes in a shop
    - `auto_deposit:bool=False` boolean to auto deposit
    - `inventory_keeps:list<int>=[]` only works if `auto_deposit` set to `True`. list of item to keep in inventory, keep a food, grooming item, and a toy is recommended in order to complete the quest
    - `skip_quests:list<str>=[]` list of quests to skip, will match quest description, such as `wheel of misfortune`, etc
    - `auto_banking:bool=True` whether should deposit np to bank if carrying more than `max_carrying_np`
    - `min_carrying_np:int=20000` minimum carrying np, used to calculate np to deposit when max carrying np is reached
    - `max_carrying_np:int=50000` maximum carrying np, will deposit to bank if carrying more than this
    '''
    def __init__(self, **kwargs):
        self.scheduler = None
        if 'scheduler' in kwargs:
            self.scheduler = kwargs.pop('scheduler')
        super().__init__("restocking", "https://www.neopets.com/inventory.phtml", **kwargs)
        self.quests = []
        self.priority = -99
        self.inventory_free = 0
        self.stock_free = 0

    def load_args(self):
        self.candidate_shop_ids = self.args.get("candidate_shops", [])
        if type(self.candidate_shop_ids) == str:
            self.candidate_shop_ids = [int(i) for i in self.candidate_shop_ids.split(',')]
        self.shop_refreshes = self.args.get("shop_refreshes", 3)
        self.refresh_interval = self.args.get("refresh_interval", 10)
        self.auto_deposit = self.args.get("auto_deposit", False)
        self.inventory_keep_items = self.args.get("inventory_keeps", [])
        self.skip_quests = self.args.get("skip_quests", [])
        self.auto_banking = self.args.get("auto_banking", True)
        self.min_profit = self.args.get("min_profit", 2000)
        self.immediate_profit = self.args.get("immediate_profit", 3500)
        self.min_carrying_np = self.args.get("min_carrying_np", 30000)
        self.max_cost = self.args.get("max_cost", 1000000)
        self.keep_stock = self.args.get("keep_stock", 5)
        return self.args

    def execute(self):
        yield from _G.rwait(2)
        if self.is_lacking_np():
            return
        line = self.page.query_selector('.inv-total-count').text_content().strip()
        r = re.search(r"(\d+) / (\d+)", line)
        self.inventory_free = 0
        if r:
            cur, total = r.groups()
            self.inventory_free = int(total) - int(cur)
        yield from self.goto("https://www.neopets.com/market.phtml?type=your")
        node = self.page.locator('img[name=keeperimage]')
        if not node:
            _G.log_warning("It seems you haven't created a shop yet, skipping restocking")
            return
        self.stock_free = int(node.locator('..').inner_text().strip().split()[-1])
        if not self.should_restocking():
            return
        shops = []
        for id in shop.NAME_DICT:
            if self.candidate_shop_ids and id not in self.candidate_shop_ids:
                continue
            shops.append(shop.NeoShop(id))
        shuffle(shops)
        _G.log_info(f"Restocking from shops: {[s.name for s in shops]}")
        try:
            for s in shops:
                if not self.should_restocking():
                    break
                s.set_page(self.page)
                for _ in range(self.shop_refreshes):
                    _G.log_info(f"Inventory/Stock free space left: {self.inventory_free} / {self.stock_free}")
                    if not self.should_restocking():
                        break
                    result = yield from self.do_shopping(s)
                    if result:
                        filename = f"{_G.BROWSER_PROFILE_DIR}/profile_{self.profile_name}/transaction_history.json"
                        s.transaction_history[-1].log(filename)
                        self.inventory_free -= 1
                        self.stock_free -= 1
                    elif result == False:
                        yield from _G.rwait(self.refresh_interval+randint(1, 5))
                    else: # result is None (empty shop)
                        break
        except Exception as e:
            utils.handle_exception(e)
        # trigger quick restocking job
        if self.scheduler:
            self.scheduler.trigger_job("quick_restock")

    def should_restocking(self):
        if self.is_lacking_np():
            _G.log_info(f"Carrying np is less than {self.min_carrying_np}, skipping restocking")
            return False
        if self.inventory_free <= 5:
            _G.log_info(f"Inventory is almost full, skipping restocking")
            return False
        if self.stock_free <= self.keep_stock:
            _G.log_info(f"Stock is almost full, skipping restocking")
            return False
        return True

    def is_lacking_np(self):
        np = action.get_available_np(self.page)
        if np <= self.min_carrying_np:
            _G.log_info(f"Carrying np is less than {self.min_carrying_np}, skipping restocking")
        return np <= self.min_carrying_np

    def do_shopping(self, nshop):
        yield from nshop.visit()
        yield from _G.rwait(2)
        nshop.scan_goods()
        yield from nshop.lookup_goods_details()
        if not nshop.goods:
            _G.log_info(f"No goods in {nshop.name}")
            return None
        goods = nshop.get_profitable_goods()
        target = None
        for g in goods:
            gn = g['name']
            if gn in player.data.shop_inventory:
                if g['price'] > self.max_cost:
                    _G.log_info(f"Skipping {gn} due to high price ({g['price']} > {self.max_cost})")
                    continue
                if player.data.shop_inventory[gn]['amount'] >= 3:
                    _G.log_info(f"Shop already stocked {gn}")
                    continue
            target = g
            break
        if not target:
            _G.log_info(f"Nothing to buy from {nshop.name}")
            return None
        result = False
        _G.log_info(f"Target: {target} profit: {target['profit']}")
        if target['profit'] >= self.immediate_profit:
            result = yield from nshop.buy_good(index=target['index'], immediate=True)
        elif target['profit'] >= self.min_profit:
            result = yield from nshop.buy_good(index=target['index'])
        else:
            _G.log_info(f"Nothing to buy from {nshop.name}")
            return None
        return result

    def calc_next_run(self):
        self.next_run = datetime.now() + timedelta(seconds=60*10+randint(30, 60*30))
        return self.next_run
