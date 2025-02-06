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

def start_buying_fiber():
    cnt = _G.ARGV.repeats
    cnt = 99 if cnt == 0 else cnt
    while cnt >= 0:
        cnt -= 1
        for pos in ((1144, 228),(910, 391),(756, 641),(631, 641),(631, 641),(631, 641),):
            Input.rclick(*pos)
            yield
            wait(0.5)

def start_drill_fiber():
    apos = ((252, 303),(252, 303),(378, 412),(1162, 648),(1167, 618),(1170, 646),(1170, 646),(656, 640),)
    atime = (5,3,6,5,40,6,18,5)
    while True:
        for i,pos in enumerate(apos):
            for _ in range(3):
                Input.rclick(*pos)
                yield from _G.rwait(0.1)
            yield from _G.rwait(atime[i])
        yield
