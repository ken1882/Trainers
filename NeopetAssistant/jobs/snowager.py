import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class SnowagerJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("snowager", "https://www.neopets.com/winter/snowager.phtml", **kwargs)
        self.last_visit = datetime(1970, 1, 1)

    def execute(self):
        self.last_visit = datetime.now()
        yield from _G.rwait(2)
        self.scroll_to(0, 200)
        yield from _G.rwait(1)
        self.click_element('#process_snowager')

    def calc_next_run(self):
        timeslots = [6, 14, 22]
        next_visit = self.last_visit + timedelta(hours=1)
        for hour in timeslots:
            timeslot_time = next_visit.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_visit < timeslot_time + timedelta(hours=1):
                self.next_run = timeslot_time
                return
        # schedule for tomorrow
        next_day_timeslot = next_visit + timedelta(days=1)
        self.next_run = next_day_timeslot.replace(hour=timeslots[0], minute=0, second=0, microsecond=0)

