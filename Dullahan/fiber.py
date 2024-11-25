import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, rwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import action
import utils
import itertools
from PIL import Image

def safe_click(x, y, dur=1, **kwargs):
    times = int(dur // 0.05)
    for _ in range(times):
        wait(0.05)
        yield
    Input.rclick(x, y, **kwargs)
    for _ in range(times):
        wait(0.05)
        yield

def start_restart_fiber():
    yield from action.restart_bs()

def start_ad_reward_fiber():
    while True:
        graphics.flush()
        a = graphics.find_object('assets/ad_reward.png')
        if a:
            Input.click(*a[0])
            for _ in range(2):
                yield from rwait(2)
                Input.rclick(*position.AD_REWARD_CLAIM)
            yield from rwait(60) # cooldown
        yield

def start_tavern_fiber():
    yield from action.back_to_main()

def start_arena_main_fiber():
    yield from action.back_to_main()

def start_arena_companion_fiber():
    yield from action.back_to_main()

def start_arena_abyss_fiber():
    yield from action.back_to_main()

def start_daily_dungeons_fiber():
    yield from action.back_to_main()

def start_daily_rewards_fiber():
    yield from action.back_to_main()

def start_awaken_upgrade_fiber():
    yield from action.back_to_main()

def start_companion_gift_fiber():
    yield from action.back_to_main()
