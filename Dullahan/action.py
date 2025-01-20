import re
import win32con
import subprocess
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, rwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import combat
import utils
import itertools
import math
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

def back_to_main():
    while not stage.is_stage('IdleMain'):
        if stage.is_stage('PowerSaving'):
            Input.click(*position.UNLOCK_POWERSAVING)
        else:
            Input.click(*position.BS_BACK)
            yield
            Input.click(*position.GENERAL_BACK)
        uwait(1)
        yield

def start_bs(wx=0, wy=0):
    if not utils.redetect_window():
        cmd = '"C:\Program Files\BlueStacks_nxt\HD-Player.exe" --instance Pie64'
        subprocess.Popen(cmd)
        yield from rwait(10)
    while True:
        print(utils.redetect_window())
        try:
            if not utils.redetect_window():
                continue
            yield from rwait(2)
            utils.move_window(wx, wy)
            yield from rwait(10)
            break
        except Exception:
            continue
    while True:
        gpos = graphics.find_object('assets/game_name.png')
        if gpos:
            _G.log_info("Restart success, starting game")
            gx = gpos[0][0] + 50
            gy = gpos[0][1] - 50
            for _ in range(3):
                Input.click(gx, gy)
                yield
            break
        yield from rwait(10)
    yield from rwait(30) # hope the game will start
    _G.log_info("Maxmize window")
    Input.click(*position.BS_MAXIMIZE_WINDOW)
    yield from rwait(5)
    utils.find_app_window()
    yield from rwait(3)
    for _ in range(3):
        Input.click(*position.BS_ROTATE_MENU)
        wait(0.1)
        Input.click(*position.BS_ROTATE_DISPLAY)
        yield
    while True:
        stg = stage.get_current_stage()
        if stage.is_stage('IdleMain'):
            break
        elif stg and 'BS' not in stg:
            yield from back_to_main()
        Input.rclick(*position.ENTER_GAME)
        yield from rwait(2)

def restart_bs():
    _G.log_info("Restarting Bluestacks by changing FPS")
    Input.click(*position.BS_SETTINGS)
    yield from rwait(5)
    col_45 = graphics.get_pixel(*position.BS_FPS_POS[45], sync=True)
    if graphics.is_color_ok(col_45, position.BS_FPS_UNSET_COLOR):
        Input.click(*position.BS_FPS_POS[45])
    else:
        Input.click(*position.BS_FPS_POS[30])
    yield from rwait(1)
    Input.click(*position.BS_SAVE_CHANGES)
    yield from rwait(5)
    Input.click(*position.BS_CONFIRM_RESTART)
    wx, wy = _G.AppRect[:2]
    yield from rwait(10)
    yield from start_bs(wx, wy)

def unique_doables(array, threshold=30):
    ret = set()
    for p in array:
        for p2 in ret:
            if math.hypot(p[0]-p2[0], p[1]-p2[1]) < threshold:
                break
        else:
            ret.add(p)
    return ret

def get_upgradeable_awakens():
    a = graphics.find_object('assets/hint_doable.png', 0.9)
    b = graphics.find_object('assets/hint_doable2.png', 0.9)
    doable_levels = unique_doables([p for p in a+b if p[0]>1600])
    doable_levels = sorted(doable_levels, key=lambda p:p[1])
    graphics.flush()

def enable_power_saving():
    for pos in ((1772, 68),(408, 618),(739, 322),):
        Input.rclick(*pos)
        yield from rwait(1.5)
