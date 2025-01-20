import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class EmploymentAgencyJob(BaseJob):
    '''
    kwargs:
    - `jellyneo:bool=True` whether to query jellyneo item db for item costs
    - `sw_loops:int=5` number of resubmits in shop wizard search (in order to get lowest price)
    - `min_profit:int=1000` minimum profit to accept job
    - `max_cost:int=10000` maximum cost for the job to accept
    '''
    def __init__(self, **kwargs):
        self.jellyneo = kwargs.get("jellyneo", True)
        self.sw_loops = kwargs.get("sw_loops", 5)
        self.min_profit = kwargs.get("min_profit", 1000)
        self.max_cost   = kwargs.get("max_cost", 10000)
        super().__init__("employment_agency", "https://www.neopets.com/faerieland/employ/employment.phtml", **kwargs)

    def execute(self):
        pass
