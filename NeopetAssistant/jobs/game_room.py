import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action
from ruffle.fashion_fever import FashionFever
from ruffle.roodoku import Roodoku

class GameRoomJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("game_room", "https://www.neopets.com/games", **kwargs)

    def load_args(self):
        self.enabled_games = self.args.get('enabled_games', ['fashion_fever'])
        if type(self.enabled_games) == str:
            self.enabled_games = self.enabled_games.split(',')
        return self.args

    def load_games(self):
        self.games = {
            "fashion_fever": FashionFever(self.page),
            "roodoku": Roodoku(self.page),
        }

    def execute(self):
        self.load_games()
        yield from self.play_all()

    def play_all(self):
        for name, game in self.games.items():
            if name not in self.enabled_games:
                continue
            _G.logger.info(f"Playing game: {name}")
            yield from game.run()
            yield from _G.rwait(3)
