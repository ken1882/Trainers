import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class AnchorManagementJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("anchor_management", "https://www.neopets.com/pirates/anchormanagement.phtml", **kwargs)

    def execute(self):
        pass