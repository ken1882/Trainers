import _G
import utils
import re
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class DailyQuestTouchJob(BaseJob):
    '''
    This job only visits daily quest page to receive the objectives, it does not complete the quest.
    '''
    def __init__(self, **kwargs):
        super().__init__("daily_quest", "https://www.neopets.com/questlog/", **kwargs)
        self.priority = 99

    def execute(self):
        yield