from operator import is_
import action
import _G
import utils
from time import sleep,time
from random import random, randint
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
CommonSkillTime = 0.5

LeftStandPos   = (32, 93)
RightStandPos  = (106, 93)

MaxCorrectionDelta = 100
TimeDeltaPerPixel  = 0.08

LoopCounter = 0

FlagPicking    = False
FlagLockSkillUse = False

ori_sleep = sleep
def sleep(sec, r=False):
    if not _G.FlagRunning or _G.FlagPaused:
        return
    while not utils.is_focused():
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
    # register_constant_skill(skill.BreathOfDivinity2, 63, False)
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
    else:
        _exec_action(skill.EarthCircle.use)

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
    Input.SendInput(kp[0])
    sleep(0.3)
    Input.SendInput(kp[1])
    sleep(0.5)

    Input.SendInput(kp[0])
    sleep(0.5)
    action.move_down(1.0)
    sleep(0.1)
    action.move_up(2.1)
    Input.SendInput(kp[1])

    sleep(0.3)
    action.move_right(0.2)
    sleep(0.2)

    Input.SendInput(kp[0])
    sleep(0.5)
    action.move_down(2.7)
    Input.SendInput(kp[1])

    sleep(0.3)
    action.move_left(0.2)
    sleep(0.2)

    Input.SendInput(kp[0])
    sleep(0.5)
    action.move_up(1.8)
    Input.SendInput(kp[1])

    FlagLockSkillUse = False

def main_loop():
    global LoopCounter,FlagLockSkillUse
    sleep(0.3, True)
    action.move_left(0.2)
    if skill.DragonMaster.is_ready():
        skill.DragonMaster.apply_cd()
        dragonmaster()
        action.blink_up()
        sleep(0.4)
        return 
    # center
    if skill.SpiderMirror.is_ready():
        _exec_action(skill.SpiderMirror.use)
        skill.SpiderMirror.apply_cd()
        sleep(2.5)
    if skill.SolarImprint.is_ready():
        _exec_action(skill.SolarImprint.use)
        skill.SolarImprint.apply_cd()
        sleep(2)
    if skill.Reincarnation.is_ready():
        skill.Reincarnation.use()
        skill.Reincarnation.apply_cd()
        sleep(0.5)
    _exec_action(skill.FireBreath.use)
    _exec_action(skill.EarthCircle.use)
    action.blink_down()
    LoopCounter += 1
    sleep(0.7)
    for _ in range(2):
        _exec_action(skill.ThunderCircle.use)
        sleep(0.8)
    _exec_action(skill.Return.use)
    # center to right
    Input.key_down(win32con.VK_RIGHT)
    for i in range(3):
        sleep(0.42)
        _exec_action(skill.ThunderCircle.use)
        sleep(0.4)
        if i < 2:
            _exec_action(skill.Teleport.use)
        else:
            Input.key_up(win32con.VK_RIGHT)
            correct_stand_pos(RightStandPos)
            action.move_right(0.2)
            sleep(0.4)
            mana_whirl()
            sleep(0.3)
            action.blink_up()
    if skill.EldasFall.is_ready():
        _exec_action(skill.EldasFall.use)
        skill.EldasFall.apply_cd()
    else:
        _exec_action(skill.EarthCircle.use)
    sleep(0.4) 
    _exec_action(skill.DragonFlash.use)
    _exec_action(skill.WindCircle.use)
    if randint(0, 1):
        skill.MagicDerbis.use()
    sleep(0.3)
    if LoopCounter > randint(2,4):
        LoopCounter = 0
        action.blink_right()
        sleep(0.3)
        _exec_action(skill.ThunderCircle.use)
        sleep(0.4)
        action.blink_left()
        sleep(0.3)
    # right to center
    Input.key_down(win32con.VK_LEFT)
    for i in range(3):
        skill.Teleport.use()
        sleep(0.2)
        if i == 1 and skill.DarkFog.is_ready():
            _exec_action(skill.DarkFog.use)
            skill.DarkFog.apply_cd()
        else:
            _exec_action(skill.ThunderCircle.use)
        sleep(0.5)
    Input.key_up(win32con.VK_LEFT)

    # center left to bottom left
    action.blink_down()
    sleep(0.4)
    action.blink_left()
    sleep(0.2)
    use_random_skill()
    sleep(0.4)
    correct_stand_pos(LeftStandPos)
    action.move_left(0.2)

    # bottom-left to upper-left
    aoe_used = False
    action.blink_up()
    sleep(0.4)
    if skill.DarkFog.is_ready():
        _exec_action(skill.DarkFog.use)
        aoe_used = True
        skill.DarkFog.apply_cd()
    else:
        _exec_action(skill.ThunderCircle.use)
    sleep(0.3)

    action.blink_up()
    sleep(0.4)
    if not skill.EldasFall.is_ready():
        _exec_action(skill.ThunderCircle.use)
        sleep(0.3)

    # upper-left to center
    action.blink_right()
    sleep(0.4)
    if skill.EldasFall.is_ready():  
        if aoe_used:
            sleep(2)
        _exec_action(skill.EldasFall.use)
        skill.EldasFall.apply_cd()
    else:    
        _exec_action(skill.ThunderCircle.use)
    sleep(0.2)
    if skill.SummonOnyxDragon.is_ready():
        action.blink_up()
        sleep(0.6)
        _exec_action(skill.SummonOnyxDragon.use)
        skill.SummonOnyxDragon.apply_cd()
        sleep(0.6)
        action.blink_down()
        sleep(0.6)
        _exec_action(skill.ThunderCircle.use)
        sleep(0.5)
    action.blink_right()
    sleep(0.4)
    _exec_action(skill.ThunderCircle.use)
    sleep(0.2)
    action.blink_down()
    sleep(0.1)


if __name__ == '__main__':
    utils.find_app_window()
    print("Player pos:", utils.get_player_pos())
    setup()
    try:
        start_constant_thread()
        sleep(2)
        while True:
            _G.FrameCount += 1
            main_loop()
    finally:
        _G.FlagRunning = False