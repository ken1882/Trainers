import _G
import utils
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action
from random import randint
from models.mixins.base_page import BasePage

class BaseFlash(BasePage):
    def __init__(self, page, url):
        super().__init__(page, url)
        self.frame = '#game_frame'
        self.locator = 'ruffle-embed'
        self.max_plays = 3
        self.played_times = 3

    def find_flash(self):
        if self.frame:
            return self.page.frame_locator(self.frame).locator(self.locator)
        return self.page.locator(self.locator)

    def playable_count(self):
        try:
            played = int(self.page.query_selector('.sent-cont').text_content().split()[-1].split('/')[0])
            self.played_times = played
            return 3 - played
        except Exception as err:
            utils.handle_exception(err)
            return 0

    def play_game(self):
        self.click_element('.play-text')
        yield from self.wait_until_page_load()
        yield from _G.rwait(30) # wait for flash to load
        self.scroll_to(node=self.page.query_selector('#game_cont'))
        if not self.find_flash():
            raise NeoError(1, "Flash player not found")
        _G.log_info("Starting game")
        yield from self.start_loop()

    def click(self, x, y, button='left', modifiers=[], random_x=(-10, 10), random_y=(-10, 10), debug=False):
        dom = self.find_flash()
        if debug:
            bb = dom.bounding_box()
            cx = bb['x'] + x
            cy = bb['y'] + y
            action.draw_debug_point(self.page, cx, cy)
        return action.locator_click(dom, x, y, button, modifiers, random_x, random_y)

    def press(self, key, delay=100, rand_delay=True):
        if rand_delay:
            delay += randint(-20, 50)
        return self.find_flash().press(key, delay=delay)

    def snapshot(self, path):
        return self.find_flash().screenshot(path=path)

    def run(self):
        yield from self.goto()
        yield from _G.rwait(3)
        if self.playable_count() <= 0:
            _G.log_info("No more plays left today")
            return
        yield from self.play_game()

    def start_loop(self):
        yield

    def start_game(self):
        yield

    def send_score(self):
        yield
