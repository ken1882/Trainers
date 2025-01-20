import _G, utils
from random import randint
from errors import NeoError
from ruffle.base_flash import BaseFlash

class FashionFever(BaseFlash):
    def __init__(self, page):
        super().__init__(page, "https://www.neopets.com/games/game.phtml?game_id=805")

    def start_loop(self):
        for _ in range(self.max_plays - self.played_times):
            yield from self.start_game()
            yield from self.send_score()
            yield from _G.rwait(1)

    def start_game(self):
        pos_ar = [(450, 320), (550, 20)] # start game, end game
        for pos in pos_ar:
            self.click(*pos)
            yield from _G.rwait(1)

    def send_score(self):
        self.click(500, 320)
        yield from _G.rwait(5)
        self.click(500, 248, random_y=(-3, 3))
