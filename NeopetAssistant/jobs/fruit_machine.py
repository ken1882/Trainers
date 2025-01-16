import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class FruitMachineJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("fruit_machine", "https://www.neopets.com/desert/fruitmachine.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        nodes = self.page.query_selector_all('input[type=submit]')
        for node in nodes:
            txt = node.get_property('value').json_value()
            if type(txt) == str and 'spin' in txt:
                node.click()
                break
        yield from _G.rwait(15) # wait for the spins
