import re
import win32con,win32gui
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, rwait, uwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import utils
import itertools
from PIL import Image
import sudoku

def start_sudoku_fiber():
    yield from sudoku.go_sudoku()

def start_test_fiber():
    yield
    _G.AppHwnd = 0x005059A
    # Input.trigger_key(win32con.VK_SPACE, duration=0.2)
    Input.trigger_key(win32con.VK_DOWN, use_msg=0)