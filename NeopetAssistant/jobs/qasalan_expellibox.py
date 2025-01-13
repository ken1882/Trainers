import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class QasalanExpelliboxJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("qasalan_expellibox", "http://ncmall.neopets.com/mall/shop.phtml?page=giveaway", **kwargs)

    def execute(self):
        pass

    def calc_next_run(self):
        curt = datetime.now()
        self.next_run = curt + timedelta(hours=7, minutes=15)
        return self.next_run
