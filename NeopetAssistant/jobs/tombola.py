import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError


class TombolaJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("tombola", "https://www.neopets.com/island/tombola.phtml", **kwargs)

    def execute(self):
        pass
