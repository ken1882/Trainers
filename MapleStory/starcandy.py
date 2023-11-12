from copy import copy
import action
import _G
import utils
from time import sleep,time
from random import random, randint, shuffle
from threading import Thread
import skill
import graphics
import Input, win32con
from random import random

SkillCDTimer    = {}
ConstantSkills  = {}
FiberQueue      = []
ConstantThread  = None
ListenerThread  = None
BaseInterval    = 0.1
LastBODTime     = 0
TeleportTime    = 0.3
CommonSkillTime = 0.5

LeftStandPos   = (28, 93)
MidStandPos    = (102, 83)
MidStandPos2   = (93, 67)
MidStandPos3   = (83, 83)
SecondFloorY   = 74

MaxCorrectionDelta = 100
TimeDeltaPerPixel  = 0.08

LoopCounter = 0

FlagPicking    = False
FlagLockSkillUse = False

SkillHaltTime = {
    skill.ThunderCircle:    0.5,
    skill.EarthCircle:      0.6,
}

RouteWeight = {}

ori_sleep = sleep
def sleep(sec, r=False):
    if not _G.FlagRunning or _G.FlagPaused:
        return
    while not utils.is_focused() and _G.FlagRunning:
        print("Unfocused, wait for 1 second")
        ori_sleep(1)
        sec = max(sec-1, 0)
    r = random()/10 if r else 0
    Input.update()
    ori_sleep(sec+r)

def start_main(pipe_in, pipe_out, *args, **kwargs):
  _G.PipeIn  = pipe_in
  _G.PipeOut = pipe_out
  try:
    while True:
      msg = pipe_out.recv()
      print(f"Subproc read: {msg}")
      if msg == _G.MsgPipeStop:
        break
  finally:
    _G.PipeIn.close()
    _G.PipeOut.close()
    print("Subproc ended")

def update_fibers():
    global FiberQueue
    _tmp = []
    for f in FiberQueue:
        if _G.resume(f):
            _tmp.append(f)
    FiberQueue = _tmp

def loop_update_fibers():
    while _G.FlagRunning:
        print(_G.FlagRunning)
        sleep(1)
        if _G.FlagPaused:
            continue
        update_fibers()

def push_async_action(func, *args, **kwargs):
    global FiberQueue
    FiberQueue.append(func(*args, **kwargs))

def start_pause_listener():
    interval = _G.FPS*2
    while _G.FlagRunning:
        Input.update()
        ori_sleep(interval)
        if not Input.is_trigger(0x50):
            continue
        print("Pause singal received")
        _G.FlagPaused ^= True
        # sleep(3)


def check_user_interrupt():
    keys = [
        0x50, # P
        win32con.VK_UP
    ]
    inted = False
    for k in keys:
        Input.update()
        if Input.is_pressed(k):
            print("User input detected, sleep for 10 seoncds")
            inted = True
    if inted:
        sleep(10)
        check_user_interrupt()

def correct_stand_pos(pos):
    px = utils.get_player_pos(True)
    print("Player pos:", px)
    if px:
        dx = px[0] - pos[0]
        if abs(dx) > MaxCorrectionDelta:
            print("Potentially wrong pos result, skip correction")
        elif dx > 0:
            action.move_left(TimeDeltaPerPixel*dx)
        else:
            action.move_right(TimeDeltaPerPixel*dx*-1)

def get_candy_location(th=0.6):
    _G.flush()
    try:
        dat = graphics.find_object('starcandy.png', th)
        if not dat:
            for i in range(7):
                dat = graphics.find_object(f"starcandy{i}.png", th)
                print(i, dat)
                if dat:
                    dat[0] = list(dat[0])
                    dat[0][1] += 100
                    break
        cx, cy = dat[0]
        pos = (cx, cy,)
    except Exception:
        _G.log_warning("Unable to find candy location")
        return (0, (0, 0))
    if cx > 1200:
        if cy > 670:
            return (3, pos)
        return (6, pos)
    elif cx < 600:
        if cy > 670:
            return (1, pos)
        return (4, pos)
    if cy > 670:
        return (2, pos)
    return (5, pos)

def get_player_location_by_plate(th=0.6):
    _G.flush()
    try:
        cx, cy = graphics.find_object('player_nameplate.png', th)[0]
        pos = (cx, cy,)
    except Exception:
        _G.log_warning("Unable to find player location")
        return (0, (0,0))
    if cx > 1200:
        if cy > 700:
            return (3, pos)
        return (6, pos)
    elif cx < 600:
        if cy > 700:
            return (1, pos)
        return (4, pos)
    if cy > 700:
        return (2, pos)
    return (5, pos)

def get_player_location_by_face(th=0.8):
    _G.flush()
    try:
        pfa = graphics.find_object('player_face.png', th)
        if not pfa:
            pfa = graphics.find_object('player_face1.png', th)
        cx, cy = pfa[0]
        cy += 150
        pos = (cx, cy,)
    except Exception:
        _G.log_warning("Unable to find player location")
        return (0, (0,0))
    if cx > 1200:
        if cy > 670:
            return (3, pos)
        return (6, pos)
    elif cx < 600:
        if cy > 670:
            return (1, pos)
        return (4, pos)
    if cy > 670:
        return (2, pos)
    return (5, pos)

LastPlayerPos = (0, (0,0))
def determine_movement():
    global LastPlayerPos
    MV_FACTOR = 210
    c_num, c_pos = get_candy_location()
    p_num, p_pos = get_player_location_by_plate()
    if p_num == 0:
        p_num, p_pos = get_player_location_by_face()
        if p_num == 0:
            _G.log_warning("Use last player pos")
            p_num, p_pos = LastPlayerPos
    if abs(c_pos[1] - p_pos[1]) > 100:
        if c_pos[1] > p_pos[1]:
            if p_num in [1,2,3]:
                p_num += 3
        if c_pos[1] < p_pos[1]:
            if p_num in [4,5,6]:
                p_num -= 3
    print(c_num, c_pos)
    print(p_num, p_pos)
    dx = c_pos[0] - p_pos[0]
    print(f"{p_num} -> {c_num}")
    LastPlayerPos = (c_num, c_pos)
    if p_num == 0 or c_num == 0:
        _G.log_warning("Unable to find route")
        return 1
    if abs(c_pos[1] - p_pos[1]) < 100:
        dur = abs(dx) / MV_FACTOR
        print(dur)
        if dx > 0:
            action.move_right(dur)
        else:
            action.move_left(dur)
    elif p_num == 1 and c_num in [4, 5, 6]:
        Input.key_down(win32con.VK_RIGHT)
        Input.key_down(win32con.VK_UP)
        sleep(2)
        Input.key_up(win32con.VK_RIGHT)
        sleep(2)
        Input.key_up(win32con.VK_UP)
        if c_num == 4:
            action.move_left(1.2)
        if c_num == 5:
            action.move_right(1.2)
        if c_num == 6:
            action.move_right(3.5)
    elif p_num == 2 and c_num in [4, 5, 6]:
        if c_num == 4 or c_num == 5:
            Input.key_down(win32con.VK_LEFT)
            Input.key_down(win32con.VK_UP)
            sleep(2.5)
            Input.key_up(win32con.VK_LEFT)
            sleep(1)
            Input.key_up(win32con.VK_UP)
            if c_num == 4:
                action.move_left(1.2)
            if c_num == 5:
                action.move_right(1.2)
        else:
            Input.key_down(win32con.VK_RIGHT)
            Input.key_down(win32con.VK_UP)
            sleep(3)
            Input.key_up(win32con.VK_RIGHT)
            sleep(1)
            Input.key_up(win32con.VK_UP)
            action.move_right(0.8)
    elif p_num == 3 and c_num in [4, 5, 6]:
        Input.key_down(win32con.VK_LEFT)
        Input.key_down(win32con.VK_UP)
        sleep(1)
        Input.key_up(win32con.VK_LEFT)
        sleep(2)
        Input.key_up(win32con.VK_UP)
        if c_num == 4:
            action.move_left(3.8)
        if c_num == 5:
            action.move_left(1.2)
        if c_num == 6:
            action.move_right(0.8)
    elif p_num == 4 and c_num in [1, 2, 3]:
        Input.key_down(win32con.VK_RIGHT)
        Input.key_down(win32con.VK_DOWN)
        sleep(2)
        Input.key_up(win32con.VK_DOWN)
        if c_num == 1:
            Input.key_up(win32con.VK_RIGHT)
            Input.key_down(win32con.VK_LEFT)
            action.jump()
            Input.key_up(win32con.VK_LEFT)
            sleep(0.7)
            action.move_left(0.5)
        if c_num == 2 or c_num == 3:
            action.jump()
            Input.key_up(win32con.VK_RIGHT)
            sleep(0.7)
            action.move_right(0.5 if c_num == 2 else 2.5)
    elif p_num == 5 and c_num in [1, 2, 3]:
        if c_num == 1 or c_num == 2:
            Input.key_down(win32con.VK_LEFT)
            Input.key_down(win32con.VK_DOWN)
            sleep(2)
            Input.key_up(win32con.VK_DOWN)
            action.jump()
            if c_num == 1:
                action.jump()
                Input.key_up(win32con.VK_LEFT)
                sleep(0.7)
                action.move_left(0.5)
            if c_num == 2:
                Input.key_up(win32con.VK_LEFT)
                Input.key_down(win32con.VK_RIGHT)
                action.jump()
                Input.key_up(win32con.VK_RIGHT)
                sleep(0.7)
                action.move_right(0.5)
        if c_num == 3:
            Input.key_down(win32con.VK_RIGHT)
            Input.key_down(win32con.VK_DOWN)
            sleep(2)
            Input.key_up(win32con.VK_DOWN)
            action.jump()
            Input.key_up(win32con.VK_RIGHT)
            sleep(0.7)
    elif p_num == 6 and c_num in [1, 2, 3]:
        Input.key_down(win32con.VK_LEFT)
        Input.key_down(win32con.VK_DOWN)
        sleep(1.5)
        Input.key_up(win32con.VK_DOWN)
        if c_num == 3:
            Input.key_up(win32con.VK_LEFT)
            Input.key_down(win32con.VK_RIGHT)
            action.jump()
            Input.key_up(win32con.VK_RIGHT)
            sleep(0.7)
        if c_num == 2 or c_num == 1:
            action.jump()
            Input.key_up(win32con.VK_LEFT)
            sleep(0.7)
            action.move_left(1 if c_num == 2 else 3)
    sleep(0.3)
    print('interact')
    action.interact()

def main_loop():
    global LoopCounter
    depth = 0
    while _G.FlagRunning:
        err = determine_movement()
        if err:
            depth += 1
            if err > 5:
                action.interact()
            depth = 0
        else:
            depth = 0
        sleep(0.5)
        _G.flush()

if __name__ == '__main__':
    utils.find_app_window()
    try:
        sleep(2)
        while True:
            _G.FrameCount += 1
            LoopCounter = 0
            main_loop()
    finally:
        _G.FlagRunning = False