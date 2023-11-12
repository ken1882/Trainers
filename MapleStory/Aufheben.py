from copy import copy
import action
import _G
import utils
from time import sleep,time
from random import random, randint, shuffle
from datetime import datetime, timedelta
from threading import Thread
import skill
import graphics
import Input, win32con
import stage
from random import random,randint

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

LastStartTime = datetime(2023, 1, 1)

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

def full_burst():
    global LoopCounter
    sequence = (
        skill.HeroicMemories,
        skill.FireBreath,
        skill.ElementalRadiance,
        skill.WindCircle,
        skill.MagicDerbis,
        skill.Return,
        skill.DragonFlash,
        skill.WindCircle,
        skill.MagicDerbis,
        skill.Return,
        skill.DragonDive,
        skill.EarthCircle,
        skill.MagicDerbis,
    )
    skill.EldasStar.use()
    sleep(1)
    _G.log_info("Elemental Radiance")
    for sk in sequence:
        print(sk.name)
        if sk == skill.ElementalRadiance:
            sleep(0.2)
        for event in Input.get_keybd_pair(sk.keycode):
            Input.SendInput(event)
        sleep(0.15)
        if sk == skill.ElementalRadiance:
            sleep(0.17)
    sleep(0.5)
    print('Soul contract')
    skill.HerosWill.use()
    sleep(0.6)
    print('Return')
    skill.Return.use()
    sleep(0.4)
    print('Dragon Slam')
    skill.DragonSlam.use()
    sleep(0.5)
    if LoopCounter % 2 == 0:
        skill.SolarImprint.use()
    else:
        skill.SpiderMirror.use()
    sleep(1)
    skill.ElementalBarrage.use()
    sleep(0.7)
    mana_whirl()
    sleep(0.6)
    skill.LucidsNightmare.use()
    sleep(0.7)
    for _ in range(4):
        skill.ManaBrust.use()
        sleep(0.7)
    # skill.LucidsNightmare.use()
    # for _ in range(3):
    #     skill.ManaBrust.use()
    #     sleep(0.7)
    # sleep(1)
    # skill.ManaBrust.use()
    # sleep(0.7)
    # skill.Return.use()
    # sleep(0.2)
    # mana_whirl()
    # sleep(0.7)
    # skill.DragonDive.use()
    # sleep(0.1)
    # skill.EarthCircle.use()
    # sleep(0.6)
    # for _ in range(2):
    #     skill.ManaBrust.use()
    #     sleep(0.7)
    # skill.Return.use()
    # sleep(0.1)
    # skill.FireBreath.use()
    # sleep(0.1)
    # skill.WindCircle.use()
    # sleep(0.5)
    # for _ in range(4):
    #     skill.ManaBrust.use()
    #     sleep(0.7)

def start_round():
    global LastStartTime,LoopCounter
    LoopCounter += 1
    _G.log_info("Round starts")
    skill.BreathOfDivinity.use()
    for _ in range(3):
        action.interact()
        sleep(1)
    _G.log_info("Wait for intro animation")
    sleep(30)
    while not stage.is_stage('Map'):
        sleep(0.03)
    _G.log_info("Start combat")
    LastStartTime = datetime.now()
    depth = 0
    wt_time = -0.5
    while depth < 5:
        _G.flush()
        _G.log_info("Detecting boss position")
        pos = graphics.find_object('auf_atk.png', threshold=0.8)
        _G.log_info("Boss position:", pos)
        if not pos:
            break
        else:
            wt_time = 0.5
        depth += 1
    _G.log_info("Move left")
    Input.key_down(win32con.VK_LEFT)
    sleep(0.5+wt_time)
    _G.log_info("Etheral form")
    skill.EtherealForm.use()
    action.move_left(1)
    Input.key_up(win32con.VK_LEFT)
    action.move_right(0.2)
    sleep(1)
    _G.log_info("Dispel")
    skill.EtherealForm.use()
    sleep(0.3)
    _G.log_info("Burst")
    full_burst()
    for _ in range(10):
        _G.flush()
        pos = graphics.find_object('exit_aufheben.png', threshold=0.8)
        if pos:
            Input.click(*pos[0])
            for _ in range(2):
                sleep(0.5)
                action.enter()
            break
    _G.log_info("Round ends")

def main_loop():
    global LoopCounter, LastStartTime
    dt = 145
    if not utils.is_focused():
        return
    if Input.is_trigger(win32con.VK_NUMPAD0, sync=True):
        _G.FlagWorking ^= True
        _G.log_info("Working:", _G.FlagWorking)
    while _G.FlagWorking and datetime.now() > LastStartTime + timedelta(seconds=dt):
        start_round()
        _G.log_info("Next start time:", (LastStartTime + timedelta(seconds=dt)).strftime('%H:%M:%S'))


if __name__ == '__main__':
    utils.find_app_window()
    try:
        sleep(2)
        while True:
            main_loop()
    finally:
        _G.FlagRunning = False