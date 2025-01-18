import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action
from ruffle.qasalan_expellibox import QasalanExpellibox

class QasalanExpelliboxJob(BaseJob):
    def __init__(self, **kwargs):
        self.player = QasalanExpellibox(None)
        super().__init__("qasalan_expellibox", "http://ncmall.neopets.com/mall/shop.phtml?page=giveaway", **kwargs)

    def set_page(self, page):
        super().set_page(page)
        self.player.set_page(page)

    def execute(self):
        yield from _G.rwait(3)
        self.scroll_to(node=self.page.query_selector('#show_NCGiveawayGame'))
        yield from _G.rwait(1)
        self.click_element('#main_div')
        yield from _G.rwait(3)
        yield from self.player.run()
        yield from _G.rwait(3)

    def calc_next_run(self):
        curt = datetime.now()
        self.next_run = curt + timedelta(hours=7, minutes=15)
        return self.next_run
