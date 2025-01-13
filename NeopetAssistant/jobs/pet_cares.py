import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class PetCaresJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("pet_cares", "https://www.neopets.com/petpetpark/daily.phtml", **kwargs)

    def execute(self):
        pass

    def feed(self):
        pass

    def play(self):
        pass

    def groom(self):
        pass