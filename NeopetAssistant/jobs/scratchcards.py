import _G
import utils
from jobs.base_job import BaseJob
from random import randint
from datetime import datetime, timedelta
from errors import NeoError

class ScratchcardsJob(BaseJob):

    LocationUrlMap = {
        'https://www.neopets.com/desert/sc/kiosk.phtml': ('desert', 'lost_desert', 'sand'),
        'https://www.neopets.com/winter/kiosk.phtml': ('ice', 'snow', 'winter'),
        'https://www.neopets.com/halloween/kiosk.phtml': ('haunted', 'spooky', 'halloween')
    }

    def __init__(self, **kwargs):
        super().__init__("scratchcards", 'https://www.neopets.com/desert/sc/kiosk.phtml', **kwargs)
        for url, locs in ScratchcardsJob.LocationUrlMap.items():
            if self.location in locs:
                self.url = url
                return
        if not self.url:
            NeoError("Invalid location for scratchcards").raise_exception()

    def load_args(self):
        self.location = self.args.get("location")
        return self.args

    def execute(self):
        yield from _G.rwait(2)
        self.click_element('input[type="submit"]', 1)

    def calc_next_run(self, shortcut=None):
        if shortcut:
            return super().calc_next_run(shortcut)
        self.next_run = datetime.now() + timedelta(hours=4) + timedelta(seconds=randint(10, 300))
        return self.next_run