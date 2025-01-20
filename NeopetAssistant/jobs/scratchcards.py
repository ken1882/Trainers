import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class ScratchcardsJob(BaseJob):

    LocationUrlMap = {
        'https://www.neopets.com/desert/sc/kiosk.phtml': ('desert', 'lost_desert', 'sand'),
        'https://www.neopets.com/winter/kiosk.phtml': ('ice', 'snow', 'winter'),
        'https://www.neopets.com/halloween/kiosk.phtml': ('haunted', 'spooky', 'halloween')
    }

    def __init__(self, **kwargs):
        location = kwargs.get("location") or ''
        for url, locs in ScratchcardsJob.LocationUrlMap.items():
            if location in locs:
                return super().__init__("scratchcards", url, **kwargs)
        raise NeoError("Invalid location for scratchcards")

    def execute(self):
        pass