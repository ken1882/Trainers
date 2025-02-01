import _G
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class LoginJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("login", "https://www.neopets.com/home", **kwargs)
        self.priority = 9999 # always check login first

    def execute(self):
        r = []
        yield from self.wait_until_element_found(lambda _: r.append(1), lambda: r, ['#navPetMenuIcon__2020'], 3)
        if not r:
            _G.log_info("Not loggin in, please login manually first, and do not close the page or tab")
            while True:
                yield from self.wait_until_element_found(lambda _: r.append(1), lambda: r,['#navPetMenuIcon__2020'], 86400)
                if not r:
                    _G.log_info("Not logged in after 24 hours, stopping job")
                    raise NeoError(1, "Not logged in")
                elif r:
                    break
        _G.log_info("Logged in")


    def calc_next_run(self, shortcut=None):
        if shortcut:
            return super().calc_next_run(shortcut)
        self.next_run = datetime.now() + timedelta(days=30)
        return self.next_run
