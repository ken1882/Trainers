import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import utils
import itertools
from PIL import Image

def start_buying_fiber():
    while True:
        pv  = sum(graphics.get_pixel(409, 457, True))
        pv += sum(graphics.get_pixel(406, 462, True))
        pv += sum(graphics.get_pixel(410, 465, True))
        if pv < 10:
            break
        Input.click(406, 456, mright=True)
        wait(0.1)
        yield
    for pos in ((395, 825),(459, 826),(532, 826),(602, 826),(659, 830),(735, 827),):
        Input.click(*pos)
        wait(0.1)
        yield

def start_upgrade_fiber():
    while True:
        for pos in ((1733, 471),(1779, 710),(1734, 566),(1785, 712),):
            Input.click(*pos)
            wait(0.1)
            yield
        Input.click(1745, 334)
        wait(1)
        yield