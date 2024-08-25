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
    cnt = 0    
    while cnt < 30:
        combat.collect_mana()
        yield
        cnt += 1

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