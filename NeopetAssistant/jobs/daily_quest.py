import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
from models import DailyQuest

class DailyQuestJob(BaseJob):
    '''
    kwargs:
    - `candidate_shops:list=[]` list of shop ids to visit
    - `auto_deposit:bool=False` boolean to auto deposit
    - `inventory_keeps:list<int>=[]` only works if `auto_deposit` set to `True`. list of item to keep in inventory, keep a food, grooming item, and a toy is recommended in order to complete the quest
    - `skip_quests:list<str>=[]` list of quests to skip, will match quest description, such as `wheel of misfortune`, etc
    - `auto_banking:bool=True` whether should deposit np to bank if carrying more than `max_carrying_np`
    - `min_carrying_np:int=20000` minimum carrying np, used to calculate np to deposit when max carrying np is reached
    - `max_carrying_np:int=50000` maximum carrying np, will deposit to bank if carrying more than this
    '''
    def __init__(self, **kwargs):
        self.candidate_shop_ids = kwargs.get("candidate_shops", [])
        self.auto_deposit = kwargs.get("auto_deposit", False)
        self.inventory_keep_items = kwargs.get("inventory_keeps", [])
        self.skip_quests = kwargs.get("skip_quests", [])
        self.auto_banking = kwargs.get("auto_banking", True)
        self.min_carrying_np = kwargs.get("min_carrying_np", 20000)
        self.max_carrying_np = kwargs.get("max_carrying_np", 50000)
        super().__init__("daily_quest", "https://www.neopets.com/dailies/index.phtml", **kwargs)
        self.priority = -99 # last job to run, normally

    def execute(self):
        pass
