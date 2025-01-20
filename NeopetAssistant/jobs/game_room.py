import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action
from ruffle.fashion_fever import FashionFever

class GameRoomJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("game_room", "https://www.neopets.com/games", **kwargs)
        self.priority = -1

    def load_games(self):
        self.games = {
            "fashion_ferver": FashionFever(self.page),
        }

    def execute(self):
        self.load_games()
        yield from self.play_all()

    def play_all(self):
        for name, game in self.games.items():
            _G.logger.info(f"Playing game: {name}")
            yield from game.run()
            yield from _G.rwait(3)
