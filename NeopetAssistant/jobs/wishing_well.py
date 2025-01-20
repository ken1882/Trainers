import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError


class WishingWellJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("wishing_well", "https://www.neopets.com/wishing.phtml", **kwargs)

    def get_wishing_item(self):
        pass
    
    def execute(self):
        pass