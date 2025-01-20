import _G
import captcha
import page_action as action
import re
import utils
import importlib
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.transaction import Transaction, NeoItem
from quest.base_quest import BaseQuest

class PurchaseItemQuest(BaseQuest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def solve(self):
        pass