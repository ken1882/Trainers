import os
from jobs.base_job import BaseJob
from errors import NeoError

class LoginJob(BaseJob):
    def __init__(self):
        super().__init__("login", "https://www.neopets.com/home")

    def execute(self):
        print("Logging in...")
        if not self.click_element('#neopass-method-login'):
            raise NeoError(2, 'Failed to neopass login')
        if not self.click_element('.signin-btn'):
            raise NeoError(2, 'Failed to neopass redirect')
        if not self.wait_until_elements_found(['button[type=submit]'], 10):
            raise NeoError(2, 'Failed to find login button')
        self.page.query_selector('input[name=email]').fill(os.getenv('NEO_EMAIL'))
        self.page.query_selector('input[name=password]').fill(os.getenv('NEO_PASSWORD'))