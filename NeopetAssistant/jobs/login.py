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
        yield from self.wait_until_element_found(lambda: r.append(1), lambda: r, ['#navPetMenuIcon__2020'], 3)
        if not r:
            _G.logger.info("Not loggin in, please login manually first, then restart the program")
            self.page.wait_for_url('https://www.neopets.com/home')
            while True:
                yield from self.wait_until_element_found(lambda: r.append(1), lambda: r,['#navPetMenuIcon__2020'], 86400)
                if not r:
                    _G.logger.info("Not logged in after 24 hours, stopping job")
                    raise NeoError(1, "Not logged in")
                elif r:
                    break
        _G.logger.info("Logged in")


    def calc_next_run(self):
        self.next_run = datetime.now() + timedelta(days=1)
        return self.next_run
