import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class AltadorCouncilJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("altador_council", "https://www.neopets.com/altador/council.phtml", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        node = self.page.query_selector("tr > td > p > map > area")
        if not node:
            return NeoError(2, "Altador Council not available, you need to finish the plot first").raise_exception()
        yield from self.goto(str(node.get_property("href")))
        yield from _G.rwait(1)
        self.click_element('input[type=submit]', 1)