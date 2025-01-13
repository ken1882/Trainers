import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class TDMBGPOPJob(BaseJob):
    '''
    The Discarded Magical Blue Grundo Plushie of Prosperity
    '''
    def __init__(self, **kwargs):
        super().__init__("tdmbgpop", "https://www.neopets.com/faerieland/tdmbgpop.phtml", **kwargs)

    def execute(self):
        pass
