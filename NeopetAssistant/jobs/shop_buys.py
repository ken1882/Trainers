import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError


class ShopBuysJob(BaseJob):
    def __init__(self, **kwargs):
        base_url = 'https://www.neopets.com/objects.phtml?type=shop&obj_type='
        self.shop_visit_map = {}
        for shop_id in kwargs.get('shops', []):
            url = base_url + shop_id
            self.shop_visit_map[url] = datetime.now() - timedelta(days=1)
        super().__init__("shop_buys", "https://www.neopets.com/market.phtml?type=your", **kwargs)

    def execute(self):
        pass
