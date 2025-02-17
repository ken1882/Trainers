import _G
import utils
import re
from jobs.base_job import BaseJob
from models import shop
from datetime import datetime, timedelta
from errors import NeoError
from models import player

QUEST_MATCH_MAP = {
    'shopping': [r"purchase(?:.|\s)*(\d+/\d+)?\s*$"],
    'wheel': [r"spin the wheel (.*)"]
}


class DailyQuestJob(BaseJob):
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
        super().__init__("daily_quest", "https://www.neopets.com/questlog/", **kwargs)
        self.quests = []

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
        self.min_carrying_np = self.args.get("min_carrying_np", 20000)
        self.max_carrying_np = self.args.get("max_carrying_np", 50000)
        self.min_profit = self.args.get("min_profit", 1000)
        self.max_cost = self.args.get("max_cost", 1000000)
        self.immediate_profit = self.args.get("immediate_profit", 3000)
        return self.args

    def execute(self):
        yield from _G.rwait(2)
        nodes = self.page.query_selector_all('.ql-task')
        for node in nodes:
            line = node.text_content().strip().lower()
            if node.query_selector('.ql-task-complete'):
                _G.log_info(f"Quest {line} already completed")
                continue
            self.quests.append(self.parse_quest(line))
        for quest in self.quests:
            _G.log_info(f"Processing quest: {quest}")
            if quest['type'] == 'wheel':
                yield from self.do_wheel_quest(quest['value'])
            elif quest['type'] == 'shopping':
                yield from self.do_shopping_quest(quest['value'])
            yield from _G.rwait(3)
        yield from self.goto(self.url)
        yield from _G.rwait(2)
        yield from self.collect_rewards()

    def parse_quest(self, line):
        _G.log_info(f"Parsing quest: {line}")
        ret = {
            'type': None,
            'value': None,
            'completed': False,
            'progress': None,
        }
        for quest_type, patterns in QUEST_MATCH_MAP.items():
            for pattern in patterns:
                match = re.match(pattern, line)
                if not match:
                    continue
                ret['type'] = quest_type
                if quest_type == 'shopping':
                    l = match.group(1)
                    if l:
                        n,m = l.split('/')
                        ret['value'] = int(m) - int(n)
                    else:
                        ret['value'] = 1
                elif quest_type == 'wheel':
                    ret['value'] = match.group(1).lower()
                break
        return ret

    def do_wheel_quest(self, wheel_name):
        _G.log_info(f"Spinning wheel: {wheel_name}")
        url = ''
        if 'excitement' in wheel_name:
            url = 'https://www.neopets.com/faerieland/wheel.phtml'
        elif 'misfortune' in wheel_name:
            url = 'https://www.neopets.com/halloween/wheel/index.phtml'
        elif 'knowledge' in wheel_name:
            url = 'https://www.neopets.com/medieval/knowledge.phtml'
        elif 'mediocrity' in wheel_name:
            url = 'https://www.neopets.com/prehistoric/mediocrity.phtml'
        elif 'monotony' in wheel_name:
            pass # skip due to waste time
        elif 'extravagance' in wheel_name:
            pass # skip due to waste money
        if not url:
            _G.log_warning(f"Wheel {wheel_name} not found or skipped")
            return
        yield from self.goto(url)
        yield from _G.rwait(2)
        self.click_element('#wheelCanvas')
        yield from _G.rwait(10) # pray for good luck
        self.click_element('#wheelCanvas')
        yield from _G.rwait(2)

    def do_shopping_quest(self, number):
        shops = []
        for id in shop.NAME_DICT:
            if self.candidate_shop_ids and id not in self.candidate_shop_ids:
                continue
            shops.append(shop.NeoShop(id))
        _G.log_info(f"Buying {number} item(s) from shops: {[s.name for s in shops]}")
        for s in shops:
            s.set_page(self.page)
            if number <= 0:
                break
            for _ in range(self.shop_refreshes):
                result = yield from self.do_shopping(s)
                if result:
                    number -= 1
                    filename = f"{_G.BROWSER_PROFILE_DIR}/profile_{self.profile_name}/transaction_history.json"
                    s.transaction_history[-1].log(filename)
                elif result == None:
                    break
                yield from _G.rwait(self.refresh_interval)

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
            if g['price'] > self.max_cost:
                _G.log_info(f"Skipping {gn} due to high price ({g['price']} > {self.max_cost})")
                continue
            if gn in player.data.shop_inventory:
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

    def collect_rewards(self):
        nodes = self.page.query_selector_all('.ql-claim')
        self.scroll_to(0, 250)
        for n in nodes:
            yield from _G.rwait(2)
            self.click_element(node=n)
            yield from _G.rwait(3)
            self.page.query_selector('#QuestLogRewardPopup').query_selector('button').click()
        yield from _G.rwait(2)
        self.page.locator('#QuestLogDailyAlert').hover()
        self.page.mouse.down()
        self.click_element('#QuestLogDailyAlert')
        yield from _G.rwait(3)
        self.page.mouse.click(30, 150)
        yield from _G.rwait(2)
        self.click_element('.ql-weekly-label')
        yield from _G.rwait(1)
        loc = self.page.locator('#QuestLogWeeklyAlert')
        if not loc.is_visible():
            return
        loc.hover()
        self.page.mouse.down()
        yield from _G.rwait(0.5)
        self.click_element('#QuestLogWeeklyAlert')
