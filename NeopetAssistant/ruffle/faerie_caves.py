import _G, utils
from random import randint
from errors import NeoError
from ruffle.base_flash import BaseFlash
from ruffle.faerie_caves_levels import LevelSolution

class FaerieCaves(BaseFlash):
    def __init__(self, page):
        super().__init__(page, "https://www.neopets.com/games/game.phtml?game_id=489")

    def start_loop(self):
        for _ in range(self.max_plays - self.played_times):
            yield from self.start_game()
            yield from self.send_score()
            yield from _G.rwait(1)

    def start_game(self):
        self.click(450, 340)

    def send_score(self):
        pass

    def solve_level(self, level):
        if level not in LevelSolution:
            raise NeoError(1, f"Level {level} not found in solution")
        solution = LevelSolution[level]
        for move in solution:
            act, val = move[0], utils.str2int(move[1:])
            if act == 'u':
                _G.log_info(f"Moving up {val} times")
                for _ in range(val):
                    self.press('ArrowUp')
                    yield
            elif act == 'd':
                _G.log_info(f"Moving down {val} times")
                for _ in range(val):
                    self.press('ArrowDown')
                    yield
            elif act == 'l':
                _G.log_info(f"Moving left {val} times")
                for _ in range(val):
                    self.press('ArrowLeft')
                    yield
            elif act == 'r':
                _G.log_info(f"Moving right {val} times")
                for _ in range(val):
                    self.press('ArrowRight')
                    yield
            elif act == 'w':
                yield from _G.rwait(val / 1000.0)
            yield
        _G.log_info(f"Level {level} solved")
