import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class BankInterestJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("bank_interest", "https://www.neopets.com/bank.phtml", **kwargs)

    def execute(self):
        pass