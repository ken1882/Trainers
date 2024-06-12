import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import combat
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

def start_daily_traven_fiber():
    ClickPos = ((1096, 756),(835, 811),)
    flag_re = False
    while True:
        yield
        curt = datetime.now()
        if flag_re and curt.minute > 55:
            utils.redetect_window()
            flag_re = False
        if curt.hour == 5 and curt.minute == 0:
            while stage.is_stage('PowerSaving'):
                yield from safe_click(256, 522)
                if curt.hour > 6:
                    break
            while not stage.is_stage('Travern'):
                if curt.hour > 6:
                    break
                yield from safe_click(449, 84)
            wait(1.5)
            for pos in ClickPos:
                yield from safe_click(*pos)
            _G.log_info("Traven seat taken")
            for _ in range(60):
                wait(1)
                yield
        elif curt.hour == 4 and curt.minute > 55:
            continue
        wait(60)
        flag_re = True
