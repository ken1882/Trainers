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
    # ListenerThread = Thread(target=start_pause_listener)
    # ListenerThread.start()
    register_constant_skill(skill.MapleBlessing, 180, False)
    register_constant_skill(skill.BreathOfDivinity, 63, False)
    # register_constant_skill(skill.Reincarnation, 240)
    # register_constant_skill(skill.DarkFog, 20)
    # register_constant_skill(skill.MasterOfNightmare, 75)
    # register_constant_skill(skill.SpiderMirror, 250)

def mana_whirl():
    skill.ManaBrust.use()
    sleep(0.1)
    Input.key_down(win32con.VK_DOWN)
    sleep(0.1)
    skill.ManaBrust.use()
    sleep(0.1)
    Input.key_up(win32con.VK_DOWN)
    sleep(0.2)

def use_random_skill():
    seed = randint(0, 1)
    if seed:
        _exec_action(skill.ThunderCircle.use)
        return skill.ThunderCircle
    else:
        _exec_action(skill.EarthCircle.use)
        return skill.EarthCircle

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

def dragonmaster():
    global FlagLockSkillUse
    FlagLockSkillUse = True
    skill.DragonMaster.apply_cd()
    kc = skill.DragonMaster.keycode
    kp = [Input.Keyboard(kc), Input.Keyboard(kc, win32con.KEYEVENTF_KEYUP)]
    action.jump()
    sleep(0.15)
    Input.SendInput(kp[0])
    sleep(0.3)
    Input.SendInput(kp[1])
    sleep(0.5)

    Input.SendInput(kp[0])
    action.move_up(2.7)
    Input.SendInput(kp[1])

    sleep(0.3)
    action.move_left(0.2)
    sleep(0.2)

    Input.SendInput(kp[0])
    sleep(0.5)
    action.move_down(2.5)
    Input.SendInput(kp[1])

    sleep(0.3)
    action.move_right(0.2)
    sleep(0.2)

    Input.SendInput(kp[0])
    sleep(0.5)
    action.move_up(1.2)
    action.move_down(1.2)
    Input.SendInput(kp[1])

    FlagLockSkillUse = False

def main_loop():
    global LoopCounter,FlagLockSkillUse
    sleep(0.3, True)
    action.move_right(0.2)
    if skill.DragonMaster.is_ready():
        sleep(0.3)
        skill.DragonMaster.apply_cd()
        dragonmaster()
        sleep(0.4)
        return 
    # center
    if skill.SpiderMirror.is_ready():
        _exec_action(skill.SpiderMirror.use)
        skill.SpiderMirror.apply_cd()
        sleep(2)
    if skill.SolarImprint.is_ready():
        _exec_action(skill.SolarImprint.use)
        skill.SolarImprint.apply_cd()
        sleep(1)
    if skill.Reincarnation.is_ready():
        skill.Reincarnation.use()
        skill.Reincarnation.apply_cd()
        sleep(CommonSkillTime)
    if skill.MasterOfNightmare.is_ready():
        skill.MasterOfNightmare.use()
        skill.MasterOfNightmare.apply_cd()
        sleep(CommonSkillTime)
    LoopCounter += 1
    if skill.DarkFog.is_ready():
        _exec_action(skill.DarkFog.use)
        skill.DarkFog.apply_cd()
        sleep(0.2)
    if utils.get_player_pos(True)[1] < SecondFloorY:
        action.blink_down()
        sleep(TeleportTime)
    r = choose_route()
    r()

def route_0():
    _sk = None
    _exec_action(skill.FireBreath.use)
    _exec_action(skill.EarthCircle.use)
    sleep(0.5)
    # center to left
    for i in range(3):
        _sk = use_random_skill()
        sleep(TeleportTime)
        action.blink_left()
        if i == 2:
            _exec_action(skill.Return.use)
        sleep(SkillHaltTime[_sk])
    sleep(0.2)
    _exec_action(skill.ThunderCircle.use)
    sleep(TeleportTime)
    # left to mid-center
    action.blink_up()
    sleep(0.4)
    _exec_action(skill.EarthCircle.use)
    sleep(0.5)
    action.move_right(0.2)
    _exec_action(skill.DragonFlash.use)
    _exec_action(skill.WindCircle.use)
    sleep(0.4)
    for i in range(3):
        if i == 1 and skill.EldasFall.is_ready():
            sleep(0.2)
            _exec_action(skill.EldasFall.use)
            skill.EldasFall.apply_cd()
        else:
            _sk = use_random_skill()
            sleep(TeleportTime)
        action.blink_right()
        sleep(SkillHaltTime[_sk])
    _exec_action(skill.ThunderCircle.use)
    sleep(0.5)
    correct_stand_pos(MidStandPos2)
    if utils.get_player_pos(True)[1] > SecondFloorY:
        action.blink_up()
        sleep(TeleportTime)
    _exec_action(skill.DragonDive.use)
    _exec_action(skill.EarthCircle.use)
    _exec_action(skill.Return.use)
    action.move_left(TeleportTime)
    _exec_action(skill.FireBreath.use)
    _exec_action(skill.EarthCircle.use)
    sleep(SkillHaltTime[skill.EarthCircle])
    # center to up then down
    action.blink_up()
    sleep(CommonSkillTime)
    _exec_action(skill.ThunderCircle.use)
    sleep(0.2)
    if skill.SummonOnyxDragon.is_ready():
        action.blink_up()
        sleep(CommonSkillTime)
        _exec_action(skill.SummonOnyxDragon.use)
        skill.SummonOnyxDragon.apply_cd()
        sleep(CommonSkillTime)
        action.blink_down()
        sleep(CommonSkillTime)
        _exec_action(skill.ThunderCircle.use)
        sleep(CommonSkillTime)
    action.blink_down()
    sleep(CommonSkillTime)
    _exec_action(skill.ThunderCircle.use)
    sleep(0.2)
    # center to right
    for _ in range(2):
        _sk = use_random_skill()
        sleep(TeleportTime)
        action.blink_right()
        sleep(SkillHaltTime[_sk])
    _exec_action(skill.Return.use)
    sleep(0.1)
    _exec_action(skill.DragonFlash.use)
    _exec_action(skill.WindCircle.use)
    sleep(0.3)
    _exec_action(skill.ThunderCircle.use)
    sleep(TeleportTime)
    action.blink_right()
    sleep(SkillHaltTime[skill.ThunderCircle])
    _exec_action(skill.ThunderCircle.use)
    # right to down then center
    sleep(SkillHaltTime[skill.ThunderCircle])
    _exec_action(skill.ThunderCircle.use)
    sleep(TeleportTime)
    action.blink_down()
    for i in range(2):
        sleep(SkillHaltTime[_sk])
        if i == 0:
            _exec_action(skill.ThunderCircle.use)
            _sk = skill.ThunderCircle
        else:
            _sk = use_random_skill()
        sleep(TeleportTime)
        action.blink_left()
    sleep(SkillHaltTime[_sk])
    _exec_action(skill.ThunderCircle.use)
    sleep(SkillHaltTime[skill.ThunderCircle])
    correct_stand_pos(MidStandPos)

def route_1():
    _sk = None
    _exec_action(skill.FireBreath.use)
    _exec_action(skill.EarthCircle.use)
    sleep(0.5)
    Input.key_down(win32con.VK_LEFT)
    sleep(0.1)
    # center to left
    _exec_action(skill.Teleport.use)
    sleep(0.7)
    _exec_action(skill.Teleport.use)
    sleep(0.3)
    Input.key_up(win32con.VK_LEFT)
    sleep(0.1)
    mana_whirl()
    Input.key_down(win32con.VK_RIGHT)
    sleep(0.1)
    _exec_action(skill.Teleport.use)
    sleep(TeleportTime*1.5)
    _exec_action(skill.Return.use)
    Input.key_up(win32con.VK_RIGHT)
    correct_stand_pos(MidStandPos3)
    action.move_left(0.2)
    _exec_action(skill.ThunderCircle.use)
    sleep(TeleportTime)
    action.blink_up()
    SkillHaltTime[skill.ThunderCircle]
    _exec_action(skill.DragonFlash.use)
    _exec_action(skill.WindCircle.use)
    sleep(0.4)
    _exec_action(skill.ThunderCircle.use)
    sleep(TeleportTime)
    action.blink_up()
    sleep(0.5)
    _exec_action(skill.ThunderCircle.use)
    sleep(0.8)
    action.move_right(0.2)
    action.blink_down()
    sleep(0.2)
    _sk = use_random_skill()
    sleep(TeleportTime)
    action.blink_right()
    sleep(SkillHaltTime[_sk])
    action.blink_down()
    sleep(0.2)
    correct_stand_pos(MidStandPos)


def choose_route():
    global RouteWeight
    upbound = sum(RouteWeight.values())
    s = randint(0, upbound-1)
    l = 0
    ret = None
    print(RouteWeight)
    print("Selected: ", s)
    for k,v in copy(RouteWeight).items():
        if l <= s and s < l+v:
            ret = k
            RouteWeight[k] = 1
        else:
            RouteWeight[k] += 1
        l += v
    print("Route:", ret)
    return ret

if __name__ == '__main__':
    RouteWeight = {
        route_0: 1,
        route_1: 1,
    }
    utils.find_app_window()
    print("Player pos:", utils.get_player_pos())
    setup()
    print(utils.get_player_pos())
    try:
        start_constant_thread()
        sleep(2)
        # route_1()
        # dragonmaster()
        # main_loop()
        while True:
            _G.FrameCount += 1
            main_loop()
    finally:
        _G.FlagRunning = False