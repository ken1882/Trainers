# WARNING: This script is supposed to be called as subprocess
from os import pipe
import action
import _G
from time import sleep,time
from random import random, randint
from threading import Thread
import skill
import Input, win32con

SkillCDTimer   = {}
ConstantSkills = {}
FiberQueue     = []
ConstantThread = None
BaseInterval = 0.1
FlagPicking    = False

ori_sleep = sleep
def sleep(sec):
    Input.update()
    ori_sleep(sec)

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

def loop_constant_skills():
    global ConstantSkills,SkillCDTimer,FlagPicking
    while _G.FlagRunning:
        sleep(_G.FPS)
        curt = time()
        for _,sk in ConstantSkills.items():
            sk,cd,stg = sk
            if stg and FlagPicking:
                continue
            if curt - SkillCDTimer[sk.name] < cd+randint(0,3):
                continue
            sk.use()
            SkillCDTimer[sk.name] = curt
            sleep(0.3)

def start_constant_thread():
    global ConstantThread
    ConstantThread = Thread(target=loop_constant_skills)
    sleep(3)
    ConstantThread.start()

def setup():
    register_constant_skill(skill.BreathOfDivinity, 31, False)
    register_constant_skill(skill.Reincarnation, 240)
    register_constant_skill(skill.DarkFog, 20)
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
        skill.EarthCircle.use()
    skill.Return.use()
    sleep(0.1)

def rand_useskill3():
    _dir = win32con.VK_LEFT if random() < 0.5 else win32con.VK_RIGHT
    _dir2 = win32con.VK_LEFT if _dir == win32con.VK_RIGHT else win32con.VK_RIGHT
    Input.key_down(_dir)
    for _ in range(2):
        skill.EarthCircle.use()
        sleep(0.5)
        skill.Teleport.use()
        sleep(0.4)
    Input.key_up(_dir)
    skill.EarthCircle.use()
    sleep(0.3)
    Input.key_down(_dir2)
    sleep(0.5)
    for _ in range(2):
        skill.EarthCircle.use()
        sleep(0.5)
        skill.Teleport.use()
        sleep(0.4)
    Input.key_up(_dir2)
    skill.EarthCircle.use()
    sleep(0.4)

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
    keys = [win32con.VK_LSHIFT, win32con.VK_UP]
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
    action.double_jumpup()
    sleep(0.25)
    skill.ThunderCircle.use()
    sleep(skill_time)
    action.move_right(1.6)
    action.blink_right()
    skill.ManaBrust.use()
    sleep(skill_time)
    action.blink_right()
    skill.ManaBrust.use()
    sleep(1)
    action.jump_down()
    sleep(1)
    skill.ThunderCircle.use()
    sleep(skill_time)
    action.blink_left()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_left()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_left()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_left()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_left()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_left()
    skill.EarthCircle.use()
    sleep(skill_time)
    sleep(0.5)
    action.double_jumpup()
    sleep(0.25)
    skill.ThunderCircle.use()
    sleep(1)
    action.jump_down()
    sleep(1)
    skill.ThunderCircle.use()
    sleep(skill_time)
    action.blink_right()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_right()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.blink_right()
    skill.EarthCircle.use()
    sleep(skill_time)
    action.move_left(0.5)
    FlagPicking = False

LoopCounter = 0
RandActions = [
    rand_useskill, rand_useskill4,
    rand_useskill2, rand_useskill3, 
    rand_useskill4, rand_useskill4
]
def main_loop():
    global LoopCounter
    sleep(0.5)
    action.move_left(0.2)
    skill.DragonFlash.use()
    skill.WindCircle.use()
    sleep(3.5)
    if random() < 0.4:
        RandActions[randint(0, len(RandActions)-1)]()
    sleep(0.6)
    action.move_right(0.2)
    skill.FireBreath.use()
    skill.EarthCircle.use()
    sleep(3)
    skill.Return.use()
    check_user_interrupt()
    LoopCounter += 1 
    if LoopCounter > 6+randint(1,4):
        pickup()
        LoopCounter = 0

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