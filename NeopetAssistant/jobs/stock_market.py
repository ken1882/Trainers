import _G
import utils
from random import sample
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class StockMarketJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("stock_market", "https://www.neopets.com/stockmarket.phtml?type=portfolio", **kwargs)

    def execute(self):
        yield from _G.rwait(2)

    def process_stock_sells(self):
        '''
        Selling shares with over 20% profit
        '''
        for n in self.page.query_selector_all('img[id]'):
            n.click()
        yield from _G.rwait(2)
        table = self.page.query_selector('#postForm')
        companies = table.query_selector_all('tr[id]')
        for com in companies:
            for row in com.query_selector_all('tr'):
                cells = row.query_selector_all('td')
                ratio = utils.str2int(cells[-2].text_content()) / 100.0
                if ratio < 0.2:
                    continue
                shares = utils.str2int(cells[0].text_content())
                cells[-1].query_selector('input').fill(str(shares))
                yield
            yield
        self.page.query_selector_all('input[type=submit]')[1].click()

    def process_stock_buys(self):
        '''
        Buying one at 15 np, up to 17
        '''
        yield from self.goto('https://www.neopets.com/stockmarket.phtml?type=buy')
        bar = self.page.query_selector('center > div > marquee')
        candidates_bull = {}
        candidates_bear = {}
        price_range = range(15, 17+1)
        for p in price_range:
            candidates_bull[p] = set()
            candidates_bear[p] = set()
        for cc in bar.query_selector_all('a'):
            code,price,delta = str(cc.text_content()).split()
            price = utils.str2int(price)
            delta = utils.str2int(delta)
            if delta < 0:
                if price in candidates_bear:
                    candidates_bear[price].add(code)
            else:
                if price in candidates_bull:
                    candidates_bull[price].add(code)
        quota = 1000
        inv_table = {}
        for p in price_range:
            if not candidates_bull[p]:
                continue
            if quota <= 0:
                break
            cn = len(candidates_bull[p])
            buys = 1000 // cn
            for c in candidates_bull[p]:
                inv_table[c] = buys
                quota -= buys
        if quota > 10:
            for p in price_range:
                if not candidates_bear[p]:
                    continue
                if quota <= 0:
                    break
                cn = len(candidates_bear[p])
                buys = 1000 // cn
                for c in candidates_bear[p]:
                    inv_table[c] = buys
                    quota -= buys
                if quota <= 0:
                    break
        inv_table[list(inv_table.keys())[0]] += quota
        for code, buys in inv_table.items():
            inps = self.page.query_selector_all('input[type=text]')
            inps[1].fill(code)
            inps[2].fill(str(buys))
            self.page.query_selector_all('input[type=submit]')[1].click()
            yield from _G.rwait(2)
            yield from self.wait_until_page_load()