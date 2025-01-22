import _G
import utils
import re
from random import randint
from jobs.base_job import BaseJob
from models import shop
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action

class GarageSaleJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("garage_sale", "https://www.neopets.com/halloween/garage.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        yield from self.scan_all_items()

    def scan_all_items(self):
        self.items = []
        container = self.page.query_selector('#items')
        nodes = container.query_selector_all('li')
