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
        self.jellyneo = kwargs.get("jellyneo", True)
        self.sw_loops = kwargs.get("sw_loops", 5)
        self.min_profit = kwargs.get("min_profit", 3000)
        self.max_cost   = kwargs.get("max_cost", 10000)
        super().__init__("employment_agency", "https://www.neopets.com/faerieland/employ/employment.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)

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
                'cost': 0,
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

    def search_sw(self, name, max_price):
        yield from self.page.goto('https://www.neopets.com/shops/wizard.phtml')
        yield from _G.rwait(2)
        self.target_shops = []
        self.page.query_selector('#shopwizard').fill(name)
        self.page.query_selector('#max_price').fill(str(max_price))
        self.click_element('#submit_wizard')