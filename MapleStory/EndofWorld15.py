import action
import _G
from time import sleep,time
from random import random, randint
from threading import Thread
import skill
import Input, win32con
from random import random

SkillCDTimer   = {}
ConstantSkills = {}
FiberQueue     = []
ConstantThread = None
ListenerThread = None
BaseInterval = 0.1
FlagPicking    = False
LastBODTime    = 0
FlagLockSkillUse = False

ori_sleep = sleep
def sleep(sec, r=False):
    if not _G.FlagRunning or _G.FlagPaused:
        return
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
    ListenerThread = Thread(target=start_pause_listener)
    ListenerThread.start()
    # register_constant_skill(skill.BreathOfDivinity2, 63, False)
    register_constant_skill(skill.BreathOfDivinity, 63, False)
    register_constant_skill(skill.Reincarnation, 240)
    # register_constant_skill(skill.DarkFog, 20)
    register_constant_skill(skill.MasterOfNightmare, 75)
    # register_constant_skill(skill.SpiderMirror, 250)

def rand_useskill():
    skill.ThunderCircle.use()
    sleep(0.3)

def rand_useskill2():
    seed = random()
    skill.Return.use()
    if seed < 0.5:
        action.move_left(0.2)
    else:
        action.move_right(0.2)
    skill.DragonSlam.use()
    sleep(0.3)
    if seed < 0.5:
        action.move_right(0.2)
    else:
        action.move_left(0.2)
    skill.ElementalBarrage.use()
    for _ in range(5):
        sleep(1)
        if random() > 0.4:
            skill.EarthCircle.use()
    skill.Return.use()
    sleep(0.1)

def rand_useskill4():
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

def pickup():
    global FlagPicking
    FlagPicking = True
    skill_time = 0.5
    for _ in range(2):
        action.blink_right()
        sleep(0.05)
        skill.EarthCircle.use()
        sleep(skill_time)
    sleep(skill_time)
    action.double_jumpup(action.DIR_LEFT)
    sleep(0.25)
    for _ in range(3):
        skill.ThunderCircle.use()
        sleep(skill_time)
    action.blink_up()
    sleep(0.1)
    skill.SummonOnyxDragon.use()
    sleep(skill_time)
    action.blink_down()
    sleep(0.1)
    for _ in range(3):
        skill.ThunderCircle.use()
        sleep(skill_time)
    action.blink_down()
    sleep(0.1)
    skill.ThunderCircle.use()
    Input.key_down(win32con.VK_LEFT)
    sleep(0.1)
    for i in range(6):
        skill.Teleport.use()
        sleep(0.1)
        if i < randint(0,3):
            skill.EarthCircle.use()
            sleep(0.05)
        else:
            skill.ManaBrust.use()
        sleep(skill_time+0.1)
    Input.key_up(win32con.VK_LEFT)
    sleep(skill_time)
    skill.MagicDerbis.use()
    Input.key_down(win32con.VK_RIGHT)
    for i in range(4):
        action.blink_right()
        sleep(skill_time)
        skill.ManaBrust.use()
        sleep(0.1)
    sleep(skill_time+0.1)
    Input.key_up(win32con.VK_RIGHT)
    action.move_left(0.4)
    FlagPicking = False
    # sleep(0.8)

LoopCounter = 0
RandActions = [
    rand_useskill, rand_useskill, rand_useskill,
    # rand_useskill2,
    rand_useskill4, rand_useskill4, rand_useskill4, rand_useskill4,
]
def _exec_action(func, *args, **kwargs):
    if not _G.FlagRunning or _G.FlagPaused:
        return
    func(*args, **kwargs)

def main_loop():
    global LoopCounter,FlagLockSkillUse
    sleep(0.5, True)
    FlagLockSkillUse = True
    _exec_action(action.blink_left)
    _exec_action(skill.DragonFlash.use)
    _exec_action(skill.WindCircle.use)
    sleep(0.3, True)
    _exec_action(action.blink_right)
    sleep(0.5)
    FlagLockSkillUse = False
    sleep(0.5)
    if not _G.FlagPaused:
        LoopCounter += 1 
    if LoopCounter % 2 == 0 and random() < 0.6:
        skill.MagicDerbis.use()
    if not _G.FlagPaused and LoopCounter > 7+randint(0,3) and time() < LastBODTime+30:
        pickup()
        LoopCounter = 0
        return
    flag_turned = False
    for _ in range(5):
        sleep(0.5, True)
        if not flag_turned and random() < 0.3:
            _exec_action(action.move_right, 0.2)
            flag_turned = True
    if random() < 0.4:
        _exec_action(RandActions[randint(0, len(RandActions)-1)])
        sleep(0.5, True)
    # sleep(0.4, True)
    if not flag_turned:
        _exec_action(action.move_right, 0.2)
    _exec_action(skill.FireBreath.use)
    _exec_action(skill.EarthCircle.use)
    sleep(3, True)
    _exec_action(skill.Return.use)
    # check_user_interrupt()

if __name__ == '__main__':
    try:
        setup()
        start_constant_thread()
        sleep(2)
        # rand_useskill4()
        # pickup()
        while True:
            main_loop()
    finally:
        _G.FlagRunning = False