import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import jellyneo as jn

class EmploymentAgencyJob(BaseJob):
    '''
    kwargs:
    - `jellyneo:bool=True` whether to query jellyneo item db for item costs
    - `sw_loops:int=5` number of resubmits in shop wizard search (in order to get lowest price)
    - `min_profit:int=1000` minimum profit to accept job
    - `max_cost:int=10000` maximum cost for the job to accept
    '''
    def __init__(self, **kwargs):
        super().__init__("employment_agency", "https://www.neopets.com/faerieland/employ/employment.phtml?type=jobs&voucher=basic", **kwargs)

    def load_args(self):
        self.sw_loops = self.args.get("sw_loops", 5)
        self.min_profit = self.args.get("min_profit", 4000)
        self.max_cost = self.args.get("max_cost", 20000)
        self.estimated_market_multipler = self.args.get("estimated_market_multipler", 2.0)
        return self.args

    @property
    def last_completed_timestamp(self):
        return self.args.get("last_completed_timestamp", 0)

    @last_completed_timestamp.setter
    def last_completed_timestamp(self, value):
        self.args['last_completed_timestamp'] = value

    @property
    def today_completed(self):
        return self.args.get("today_completed", 0)

    @today_completed.setter
    def today_completed(self, value):
        self.args['today_completed'] = value

    def execute(self):
        yield from _G.rwait(2)
        self.job_done = False
        self.page_index = 0
        target_offer = None
        while not target_offer:
            yield from self.scan_offers()
            self.page_index += 10
            yield from self.goto(self.url + f"&start={self.page_index}")
            if self.has_content('page is empty'):
                break

    def scan_quests(self):
        panel = self.page.query_selector('.content')
        nodes = panel.query_selector_all('tr > td')
        idx = 3
        self.quests = []
        jn_args = []
        while idx < len(nodes):
            eles = nodes[idx].inner_html().split('<br>')
            name = eles[0].split('</b>')[-1].strip()
            amount = utils.str2int(eles[0].split('</b>')[0].strip())
            reward = utils.str2int(eles[-1].split('</b>')[-1].strip())
            jn_args.append(name)
            self.quests.append({
                'name': name,
                'amount': amount,
                'reward': reward,
                'cost': 10**8,
            })
            idx += 5
        jn_working = True
        jn.batch_search(jn_args, False)
        while jn_working:
            yield
            jn_working = jn.is_busy()
        for quest in self.quests:
            item = jn.get_item_details_by_name(quest['name'])
            if item:
                quest['cost'] = item['price'] * quest['amount']
        self.quests = sorted(self.quests, key=lambda x: x['reward'] - x['cost'], reverse=True)
        msg = "Quests:\n"
        for q in self.quests:
            msg += f"{q['name']} {q['reward'] - q['cost']} <="
            msg += f" - ({q['cost'] // q['amount']} * {q['amount']} -> {q['cost']})"
            msg += f" + {q['reward']}\n"
        _G.log_info(msg)

    def search_sw(self, name, max_price):
        yield from self.page.goto('https://www.neopets.com/shops/wizard.phtml')
        yield from _G.rwait(2)
        self.target_shops = []
        self.page.query_selector('#shopwizard').fill(name)
        self.page.query_selector('#max_price').fill(str(max_price))
        self.click_element('#submit_wizard')

    def turn_in(self):
        if not self.target_offer:
            return
        if not self.job_done:
            return
        last_completed_time = datetime.fromtimestamp(self.last_completed_timestamp)
        curt = utils.localt2nst(datetime.now())
        if last_completed_time.day == curt.day and last_completed_time.month == curt.month and last_completed_time.year == curt.year:
            self.today_completed += 1
        else:
            self.today_completed = 1
        self.last_completed_timestamp = utils.localt2nst(datetime.now()).timestamp()

    def calc_next_run(self, shortcut=None):
        if shortcut:
            return super().calc_next_run(shortcut)
        if self.today_completed >= 5:
            return super().calc_next_run('daily')