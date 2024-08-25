import _G, utils
import Input
import position
import stage, graphics
from act import Act
from collections import deque
from threading import Thread
from random import random

UPDATE_INTERVAL = 2
STAGE_CHCEK_INTERVAL = 30
FLAG_CHECK_MANA_ASYNC = True
MANA_CHECK_INTERVAL = 3

TickCnt = 0
ManaCheckCnt = 0
ManaVal = 0
ManaCheckThread = None
ManaRefillMode = False
FlagLoopStarted = False
ActionQueue = deque()


def get_mana(remode=False):
    ret = -9999
    last_result = 9999
    while _G.FlagRunning and _G.FlagWorking and abs(last_result - ret) > 150 and (ret < 0 or ret > 500):
        last_result = ret
        if _G.FlagPaused:
            continue
        try:
            if remode:
                ret = int(utils.ocr_rect(position.ManaRectRefill, 'mp.png', lang='eng').split('/')[0])
            elif _G.ARGV.tournment:
                ret = int(utils.ocr_rect(position.ManaRectTournment, 'mp.png', num_only=True))
            else:
                ret = int(utils.ocr_rect(position.ManaRectNormal, 'mp.png', num_only=True))
        except Exception as err:
            print(err)
    return ret

def collect_mana():
    def tap(x,y):
        mx = int(x) + random.randint(-8, 8)
        my = int(y) + random.randint(-8, 8)
        Input.mouse_down(mx, my)
        _G.wait(0.01)
        Input.mouse_up(mx, my)
    for pos in position.ManaCirclePos:
        tap(*pos)

def process_mana_refill():
    global ManaRefillMode
    _G.log_info("Processing mana refill")
    ManaRefillMode = True
    while not stage.mana_refill_stage():
        Input.rclick(*position.EnterManaRefill)
        _G.wait(0.1)
        yield
    if FLAG_CHECK_MANA_ASYNC:
        while ManaVal >= 0 and ManaVal < 300:
            for _ in range(2):
                collect_mana()
                yield
    else:
        mp = None
        while mp == None:
            mp = get_mana(True)
            yield
        while mp < 300:
            collect_mana()
            yield
    _G.log_info("Exit mana refill")
    for _ in range(3):
        Input.rclick(*position.GeneralBack)
        yield
        _G.wait(0.03)
    ManaRefillMode = False

def is_skill_usable(x, y):
    return sum(graphics.get_pixel(x,y, True)) > 250

def is_core_attack():
    return False

def is_standby_phase():
    return False

def should_mana_refilled():
    global ManaVal
    if FLAG_CHECK_MANA_ASYNC:
        return ManaVal >= 0 and ManaVal < 200
    return get_mana()

def process_standby_buff():
    yield

def process_core_attack():
    yield

def determine_memory_use():
    i = 0
    for x in range(5):
        for y in range(5):
            mx = position.CardCDChecks[i][0] + x
            my = position.CardCDChecks[i][1] + y
            if is_skill_usable(mx, my):
                return i

def determine_mana_refill():
    global ManaCheckCnt, ActionQueue
    if 'MP_REFILL' in ActionQueue:
        return
    ManaCheckCnt += 1
    if FLAG_CHECK_MANA_ASYNC:
        if ManaVal >= 0 and ManaVal < 200:
            ActionQueue.append(Act('FLAG', value='MP_REFILL'))
            ManaCheckCnt = 0
            return
    elif ManaCheckCnt >= MANA_CHECK_INTERVAL:
        mp = None
        while mp == None:
            mp = get_mana()
            yield
        if mp >= 0 and mp < 200:
            ActionQueue.append(Act('FLAG', value='MP_REFILL'))
            ManaCheckCnt = 0
            return

def main_loop():
    if _G.ARGV.tournment:
        determine_mana_refill()
        if is_core_attack():
            ActionQueue.append(Act('FLAG', value='ATTACK_PHASE'))
        elif is_standby_phase():
            ActionQueue.append(Act('FLAG', value='STANDBY_PHASE'))
    yield from process_action()

def process_action():
    global ActionQueue
    act = ActionQueue.popleft()
    if act.kind == 'FLAG':
        if act.value == 'MP_REFILL':
            yield from process_mana_refill()
        elif act.value == 'ATTACK_PHASE':
            yield from process_core_attack()
        elif act.value == 'STANDBY_PHASE':
            yield from process_standby_buff()
        else:
            _G.log_warning(f"Unknown action flag:", vars(act))
    else:
        # Default action
        midx = determine_memory_use()
        if midx == None:
            return
        _G.log_info(f"Use card#{midx}")
        Input.rclick(*position.MemoryCards[midx])
    yield

def update_mana_async():
    global ManaVal,FlagLoopStarted
    while FlagLoopStarted and _G.FlagRunning and _G.FlagWorking:
        if _G.FlagPaused:
            continue
        mp = None
        print("Refill mode:", ManaRefillMode)
        while mp == None:
            mp = get_mana(ManaRefillMode)
            _G.wait(0.3)
        ManaVal = mp
        _G.log_info("MP:", ManaVal)
        _G.wait(MANA_CHECK_INTERVAL*0.1)

def setup():
    global ManaCheckThread
    if FLAG_CHECK_MANA_ASYNC:
        ManaCheckThread = Thread(target=update_mana_async)
        ManaCheckThread.start()

def main():
    global TickCnt, FlagLoopStarted
    stage_ok = False
    FlagLoopStarted = True
    try:
        setup()
        while _G.ARGV.tournment:
            yield from main_loop()
        while not _G.ARGV.tournment:
            yield
            TickCnt += 1
            if TickCnt % STAGE_CHCEK_INTERVAL == 0:
                for _ in range(3):
                    ok = stage.is_stage('Combat')
                    yield
                    if ok:
                        stage_ok = True
                        break
                else:
                    stage_ok = False
            if not stage_ok or TickCnt % UPDATE_INTERVAL != 0:
                continue
            yield from main_loop()
    finally:
        FlagLoopStarted = False
