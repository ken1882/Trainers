import _G, utils
from random import randint
from errors import NeoError
from ruffle.base_flash import BaseFlash

class QasalanExpellibox(BaseFlash):
    def __init__(self, page):
        super().__init__(page, '')
        self.frame = ''
        self.locator = '#main_div'

    def run(self):
        yield from _G.rwait(1)
        self.click(350, 500, debug=1)
        yield from _G.rwait(3)
