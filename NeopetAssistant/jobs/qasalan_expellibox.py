import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action
from ruffle.qasalan_expellibox import QasalanExpellibox

class QasalanExpelliboxJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("qasalan_expellibox", "http://ncmall.neopets.com/mall/shop.phtml?page=giveaway", **kwargs)
        self.player = QasalanExpellibox(self.page)

    def execute(self):
        yield from _G.rwait(2)
        node = self.page.query_selector('#main_div')
        self.scroll_to(node=node)
        yield from _G.rwait(1)
        self.player.find_flash()
        yield from self.player.run()
        yield from _G.rwait(5)

    def calc_next_run(self):
        curt = datetime.now()
        self.next_run = curt + timedelta(hours=7, minutes=15)
        return self.next_run
