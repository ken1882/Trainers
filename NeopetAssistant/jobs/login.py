import _G
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class LoginJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("login", "https://www.neopets.com/home", **kwargs)

    def execute(self):
        if not self.wait_until_element_found('#navPetMenuIcon__2020', 3):
            _G.logger.info("You're not logged in, please manually login")
        if not self.wait_until_element_found('#navPetMenuIcon__2020', 86400):
            _G.logger.info("Not logged in after 24 hours, stopping job")
            raise NeoError(1, "Not logged in")

    def calc_next_run(self):
        self.next_run = datetime.now() + timedelta(days=1)
        return self.next_run
