import _G, utils
from random import randint
from errors import NeoError
from ruffle.base_flash import BaseFlash

class QasalanExpellibox(BaseFlash):
    def __init__(self, page):
        super().__init__(page)

    def run(self):
        self.click(250, 300)
        yield from self._G.rwait(3)
