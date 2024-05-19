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

def start_click_fiber():
    times = _G.ARGV.repeats or 0
    interval = _G.ARGV.index / 1000
    rrange = (_G.ARGV.jndex, _G.ARGV.jndex)
    if times == 0:
        times = 0x7fffffffffffffff
    flag_working = True
    ox, oy = 0, 0
    if _G.ARGV.jndex:
        ox, oy = Input.get_cursor_pos(False)
        print(ox, oy)
    while times and flag_working and utils.is_focused():
        Input.rclick(ox, oy, use_msg=False, app_offset=False, rrange=rrange)
        yield from rwait(interval)
        yield
