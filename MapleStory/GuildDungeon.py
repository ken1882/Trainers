from copy import copy
import action
import _G
import utils
from time import sleep,time
from random import random, randint, shuffle
from threading import Thread
import skill
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

def register_constant_skill(skill, interval, stagger=True):
    global ConstantSkills,SkillCDTimer
    ConstantSkills[skill.name] = [skill, interval, stagger]
    SkillCDTimer[skill.name] = 0

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

def loop_constant_skills():
    global ConstantSkills,SkillCDTimer,FlagPicking,LastBODTime
    while _G.FlagRunning:
        sleep(_G.FPS)
        curt = time()
        for _,sk in ConstantSkills.items():
            sk,cd,stg = sk
            if FlagLockSkillUse or (stg and FlagPicking):
                continue
            if curt - SkillCDTimer[sk.name] < cd+randint(0,2):
                continue
            sk.use()
            if sk.name == skill.BreathOfDivinity.name:
                LastBODTime = time()
                print('Use BOD')
            SkillCDTimer[sk.name] = curt
            sleep(0.3)

def start_constant_thread():
    global ConstantThread
    ConstantThread = Thread(target=loop_constant_skills)
    sleep(3)
    ConstantThread.start()

def setup():
    global ListenerThread
    skill.SpiderMirror.apply_cd()
    skill.SolarImprint.apply_cd()
    skill.DragonMaster.apply_cd()
    skill.EldasFall.apply_cd()
    skill.DarkFog.apply_cd()
    skill.SummonOnyxDragon.apply_cd()
    register_constant_skill(skill.MapleBlessing, 180, False)
    register_constant_skill(skill.BreathOfDivinity, 63, False)

def mana_whirl():
    skill.ManaBrust.use()
    sleep(0.1)
    Input.key_down(win32con.VK_DOWN)
    sleep(0.1)
    skill.ManaBrust.use()
    sleep(0.1)
    Input.key_up(win32con.VK_DOWN)
    sleep(0.2)

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

def _exec_action(func, *args, **kwargs):
    global FlagLockSkillUse
    if not _G.FlagRunning or _G.FlagPaused:
        return
    FlagLockSkillUse = True
    func(*args, **kwargs)
    FlagLockSkillUse = False

def main_loop():
    global LoopCounter
    LoopCounter += 1
    action.move_left(0.2)
    _exec_action(skill.FireBreath.use)
    _exec_action(skill.EarthCircle.use)
    sleep(1)
    action.blink_down()
    sleep(1.8)
    _exec_action(skill.Return.use)
    sleep(0.5)
    action.blink_up()
    sleep(0.5)
    action.move_right(0.2)
    _exec_action(skill.DragonFlash.use)
    _exec_action(skill.WindCircle.use)
    sleep(3)
    _exec_action(skill.Return.use)
    sleep(0.5)
    if LoopCounter % 3 == 0:
        _exec_action(skill.MagicDerbis.use)



if __name__ == '__main__':
    utils.find_app_window()
    print("Player pos:", utils.get_player_pos())
    setup()
    print(utils.get_player_pos())
    try:
        start_constant_thread()
        sleep(2)
        while True:
            _G.FrameCount += 1
            LoopCounter = 0
            main_loop()
    finally:
        _G.FlagRunning = False