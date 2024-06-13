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
    ar = (406, 456),(319, 498),(487, 491)
    while True:
        pv  = sum(graphics.get_pixel(409, 457, True))
        pv += sum(graphics.get_pixel(406, 462, True))
        if pv < 10:
            break
        for pos in ar:
            Input.click(*pos)
            wait(0.08)
            yield
        wait(0.1)
        yield