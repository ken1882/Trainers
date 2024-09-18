import _G, utils
import Input
import position
import stage, graphics
from act import Act
from collections import deque
from threading import Thread
from datetime import datetime, timedelta
import random

UPDATE_INTERVAL = 2
STAGE_CHCEK_INTERVAL = 30
FLAG_CHECK_MANA_ASYNC = True
MANA_CHECK_INTERVAL = 3

TickCnt = 0
ManaCheckCnt = 0
ManaVal = -999
ManaCheckThread = None
ManaRefillMode = False
FlagLoopStarted = False
LastRecoverTime = datetime(1970, 1, 1)
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

def is_mp_enough(mp):
    return mp >= 0 and mp > 300 and mp < 500

def process_mana_refill():
    global ManaRefillMode, ManaVal, LastRecoverTime
    _G.log_info("Processing mana refill")
    while not stage.is_stage('ManaRefill'):
        Input.rclick(*position.EnterManaRefill)
        _G.wait(0.1)
        yield
        if is_mp_enough(ManaVal):
            yield from abort_mana_refill()
            return
    ManaRefillMode = True
    _G.log_info("Collecting Mana")
    exit_depth = 0
    if FLAG_CHECK_MANA_ASYNC:
        while True:
            for _ in range(2):
                collect_mana()
                yield
            if is_mp_enough(ManaVal):
                break
            if not stage.is_stage('ManaRefill'):
                exit_depth += 1
                if exit_depth > 3:
                    break
            else:
                exit_depth = 0
    else:
        mp = None
        while mp == None:
            mp = get_mana(True)
            yield
        while not is_mp_enough(mp):
            collect_mana()
            yield
    LastRecoverTime = datetime.now()
    yield from abort_mana_refill()

def abort_mana_refill():
    global ManaRefillMode
    _G.log_info("Exit mana refill")
    dep = 0
    while dep < 5:
        yield
        for pos in position.ManaCirclePos:
            Input.rclick(*position.GeneralBack)
            yield
            Input.rclick(*pos)
            yield
        if not stage.is_stage('ManaRefill'):
            dep += 1
        else:
            dep = 0
    ManaRefillMode = False

def is_skill_usable(x, y):
    return sum(graphics.get_pixel(x,y, True)) > 250

def is_core_attack():
    return stage.is_stage('AttackPhase')

def is_standby_phase():
    return stage.is_stage('StandbyPhase')

def should_mana_refilled():
    global ManaVal, ManaCheckCnt, LastRecoverTime
    if datetime.now() - LastRecoverTime < timedelta(seconds=15):
        return False
    ManaCheckCnt += 1
    if FLAG_CHECK_MANA_ASYNC:
        if ManaVal >= 0 and ManaVal <= 100:
            return True
    elif ManaCheckCnt >= MANA_CHECK_INTERVAL:
        mp = None
        ManaCheckCnt = 0
        while mp == None:
            mp = get_mana()
        if mp >= 0 and mp <= 100:
            return True
    return False

def process_standby_buff():
    for pos in position.StandbyBuffPos:
        Input.rclick(*pos)
        yield

def process_core_attack():
    for pos in position.MemoryCards[1:-1]:
        Input.rclick(*pos)
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
    global ActionQueue, ManaVal
    if any(['MP_REFILL' == a for a in ActionQueue if a.kind == 'FLAG']):
        return True
    if should_mana_refilled():
        _G.log_info("requested mana refill", ManaVal)
        ActionQueue.append(Act('FLAG', value='MP_REFILL'))
        return True
    return False
    
def main_loop():
    yield
    if _G.ARGV.tournment:
        if determine_mana_refill():
            pass
        elif is_core_attack():
            ActionQueue.append(Act('FLAG', value='ATTACK_PHASE'))
        elif is_standby_phase():
            ActionQueue.append(Act('FLAG', value='STANDBY_PHASE'))
    yield from process_action()

def process_action():
    global ActionQueue
    act = ActionQueue.popleft() if ActionQueue else Act('None')
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
    interval = MANA_CHECK_INTERVAL*0.1
    while FlagLoopStarted and _G.FlagRunning and _G.FlagWorking:
        if _G.FlagPaused:
            continue
        mp = None
        print("Refill mode:", ManaRefillMode)
        while mp == None:
            _G.flush()
            mp = get_mana(ManaRefillMode)
        ManaVal = mp
        _G.log_info("MP:", ManaVal)
        _G.wait(interval)

def setup():
    global ManaCheckThread
    if FLAG_CHECK_MANA_ASYNC and _G.ARGV.tournment:
        ManaCheckThread = Thread(target=update_mana_async, daemon=True)
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
