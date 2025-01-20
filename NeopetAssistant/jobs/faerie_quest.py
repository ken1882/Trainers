import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class FaerieQuestJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("faerie_quest", "https://www.neopets.com/quests.phtml", **kwargs)

    def execute(self):
        pass
