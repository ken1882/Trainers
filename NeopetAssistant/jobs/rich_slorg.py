import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class RichSlorgJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("rich_slorg", "https://www.neopets.com/shop_of_offers.phtml?slorg_payout=yes", **kwargs)

    def execute(self):
        yield from _G.rwait(3)
