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


def start_star_fiber():
    _G.flush()
    cnt = 0
    while True:
        Input.click(359, 516)
        yield
        wait(0.5)
        objs = graphics.find_object('magic.png')
        cnt = len(objs)
        print(cnt, objs)
        if cnt > 3 and all([p[1] > 300 for p in objs]):
            break

def start_roll_fiber():
    _G.flush()
    cnt = 0
    while True:
        yield
        wait(1)
        Input.click(955, 543)
        for _ in range(10):
            yield
            wait(0.5)
        objs = graphics.find_object('crit.png', 0.7)
        cnt = len(objs)
        print(cnt, objs)
        if cnt >= 5:
            Input.click(1113, 530)
            break
        else:
            Input.click(803, 528)
            wait(0.5)
