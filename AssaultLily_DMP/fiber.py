import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, rwait, uwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import utils
import itertools
from PIL import Image

import combat

def start_mana_refill_fiber():
    def tap(x,y):
        hwnd = _G.AppHwnd
        Input.mouse_down(x, y, False, True, hwnd)
        _G.wait(0.01)
        Input.mouse_up(x, y, False, True, hwnd)
    while True:
        for pos in position.ManaCirclePos:
            tap(*pos)
            yield

def start_combat_fiber():
    yield from combat.main()

def start_heartbeat_fiber():
    cnt = 0
    while True:
        cnt += 1
        yield
        if cnt > 1000:
            Input.rclick(125,110, use_msg=True, app_offset=False)
            cnt = 0