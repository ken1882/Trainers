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
    while times and flag_working:
        Input.click(ox, oy, use_msg=False, app_offset=False)
        wait(interval)
        yield

def start_mccp_fiber():
    for _ in range(9):
        yield
        Input.mclick(0, 0, use_msg=False, app_offset=False)
        mx, my = Input.get_cursor_pos(False)
        Input.set_cursor_pos(mx+48, my, use_msg=False, app_offset=False)
        Input.click(0, 0, use_msg=False, app_offset=False)

def start_assign_fiber():
    ox, oy = Input.get_cursor_pos(False)
    while 1:
        yield
        my = oy
        for _ in range(3):
            Input.click(ox, my, use_msg=False, app_offset=False)
            yield
            wait(0.1)
            my += 25
        for _ in range(2):
            Input.trigger_key(win32con.VK_TAB, use_msg=False)
            yield
            wait(0.1)
        for _ in range(100):
            yield
            wait(0.1)

def start_accept_fiber():
    stages = [
        (
            ((1006, 837),(706, 822),(1626, 844),(1146, 821),),
            ((41, 127, 167),(41, 127, 167),(41, 127, 167),(41, 127, 167),)
        ),
        (
            ((824, 773),(1255, 785),(1080, 785),),
            ((41, 127, 167),(41, 127, 167),(41, 127, 167),)
        ),
        (
            ((830, 833),(1324, 844),(1562, 831),),
            ((41, 127, 167),(41, 127, 167),(41, 127, 167),)
        ),
        (
            ((1043, 821),(1442, 820),(821, 816),),
            ((45, 134, 176),(45, 134, 176),(45, 134, 176),)
        )
    ]
    while 1:
        yield
        for pix, col in stages:
            if graphics.is_pixel_match(pix, col, True):
                Input.click(pix[1][0], pix[1][1], use_msg=False, app_offset=False)
                break
        for _ in range(10):
            yield
            wait(0.1)

def start_palworld_fiber():
    while 1:
        yield
        if Input.is_trigger(win32con.VK_RBUTTON):
            mpos = Input.get_cursor_pos(False)
            wait(0.2)
            Input.click(1102, 975, use_msg=False, app_offset=False)
            wait(0.1)
            Input.set_cursor_pos(mpos[0], mpos[1], use_msg=False, app_offset=False)