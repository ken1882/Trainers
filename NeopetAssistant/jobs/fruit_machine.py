import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class FruitMachineJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("fruit_machine", "https://www.neopets.com/desert/fruitmachine.phtml", **kwargs)

    def execute(self):
        pass
