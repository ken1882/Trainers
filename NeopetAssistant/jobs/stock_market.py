import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class StockMarketJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("stock_market", "https://www.neopets.com/stockmarket.phtml?type=list&search=", **kwargs)

    def execute(self):
        pass
    
    def determine_stock_sells(self):
        pass
    
    def determine_stock_buys(self):
        pass