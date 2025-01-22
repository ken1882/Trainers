import _G
import utils
import re
from random import randint
from jobs.base_job import BaseJob
from models import shop
from datetime import datetime, timedelta
from errors import NeoError
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

    def load_args(self):
        self.candidate_shop_ids = self.args.get("candidate_shops", [])
        self.shop_refreshes = self.args.get("shop_refreshes", 3)
        self.refresh_interval = self.args.get("refresh_interval", 10)
        self.auto_deposit = self.args.get("auto_deposit", False)
        self.inventory_keep_items = self.args.get("inventory_keeps", [])
        self.skip_quests = self.args.get("skip_quests", [])
        self.auto_banking = self.args.get("auto_banking", True)
        self.min_profit = self.args.get("min_profit", 2000)
        self.immediate_profit = self.args.get("immediate_profit", 3000)
        self.min_carrying_np = self.args.get("min_carrying_np", 20000)
        return self.args

    def execute(self):
        yield from _G.rwait(2)
        if self.is_lacking_np():
            return
        line = self.page.query_selector('.inv-total-count').text_content().strip()
        r = re.search(r"(\d+) / (\d+)", line)
        number = 0
        if r:
            cur, total = r.groups()
            number = int(total) - int(cur)
        shops = []
        for id in shop.NAME_DICT:
            if self.candidate_shop_ids and id not in self.candidate_shop_ids:
                continue
            shops.append(shop.NeoShop(id))
        _G.log_info(f"Restocking from shops: {[s.name for s in shops]}")
        for s in shops:
            s.set_page(self.page)
            for _ in range(self.shop_refreshes):
                _G.log_info(f"Inventory free space left: {number}")
                if number < 0 or self.is_lacking_np():
                    return
                result = yield from self.do_shopping(s)
                if result:
                    filename = f"{_G.BROWSER_PROFILE_DIR}/profile_{self.profile_name}/transaction_history.json"
                    s.transaction_history[-1].log(filename)
                    number -= 1
                elif result == False:
                    yield from _G.rwait(self.refresh_interval+randint(1, 5))
                else: # result is None (empty shop)
                    break
        # trigger quick restocking job
        if self.scheduler:
            self.scheduler.trigger_job("quick_restock")

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
        target = nshop.get_profitable_goods()[0]
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
