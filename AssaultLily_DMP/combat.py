import _G, utils
import Input
import position
import stage, graphics
from threading import Thread

UPDATE_INTERVAL = 2
STAGE_CHCEK_INTERVAL = 30
FLAG_CHECK_MANA_ASYNC = True
MANA_CHECK_INTERVAL = 3

TickCnt = 0
ManaCheckCnt = 0
ManaVal = 0
ManaCheckThread = None
ManaRefillMode = False

def get_mana(remode=False):
    ret = -1
    while _G.FlagRunning and _G.FlagWorking and (ret < 0 or ret > 999):
        if _G.FlagPaused:
            continue
        try:
            if remode:
                ret = int(utils.ocr_rect(position.ManaRectRefill, 'mp.png', lang='eng').split('/')[0])
            else:
                ret = int(utils.ocr_rect(position.ManaRectNormal, 'mp.png', num_only=True))
        except Exception as err:
            print(err)
    return ret
    

def process_mana_refill():
    global ManaRefillMode
    def tap(x,y):
        hwnd = _G.AppHwnd
        Input.mouse_down(x, y, False, True, hwnd)
        _G.wait(0.01)
        Input.mouse_up(x, y, False, True, hwnd)
    _G.log_info("Processing mana refill")
    ManaRefillMode = True
    for _ in range(3):
        Input.rclick(*position.EnterManaRefill)
        _G.wait(0.1)
        yield
    if FLAG_CHECK_MANA_ASYNC:
        while ManaVal < 300:
            for pos in position.ManaCirclePos:
                tap(*pos)
                yield
    else:
        mp = None
        while mp == None:
            mp = get_mana(True)
            yield
        while mp < 300:
            for pos in position.ManaCirclePos:
                tap(*pos)
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

def process_core_attack():
    pass

def determine_memory_use():
    i = 0
    for x in range(5):
        for y in range(5):
            mx = position.CardCDChecks[i][0] + x
            my = position.CardCDChecks[i][1] + y
            if is_skill_usable(mx, my):
                return i

def determine_action():
    global ManaCheckCnt
    if _G.ARGV.tournment:
        if FLAG_CHECK_MANA_ASYNC and ManaVal < 100:
            yield from process_mana_refill()
            ManaCheckCnt = 0
            return
        elif ManaCheckCnt >= MANA_CHECK_INTERVAL:
            mp = None
            while mp == None:
                mp = get_mana(True)
                yield
            if mp < 100:
                yield from process_mana_refill()
                ManaCheckCnt = 0
                return
        elif is_core_attack():
            yield from process_core_attack()
            return
    ManaCheckCnt += 1
    midx = determine_memory_use()
    if midx == None:
        return
    _G.log_info(f"Use card#{midx}")
    Input.rclick(*position.MemoryCards[midx])
    _G.wait(0.1)

def update_mana_async():
    global ManaVal
    while _G.FlagRunning and _G.FlagWorking:
        if _G.FlagPaused:
            continue
        mp = None
        while mp == None:
            mp = get_mana(ManaRefillMode)
            _G.wait(0.3)
        ManaVal = mp
        _G.log_info("MP:", ManaVal)
        _G.wait(MANA_CHECK_INTERVAL*0.1)

def main():
    global TickCnt, ManaCheckThread
    stage_ok = False
    if FLAG_CHECK_MANA_ASYNC:
        ManaCheckThread = Thread(target=update_mana_async)
        ManaCheckThread.start()
    while True:
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
        yield from determine_action()
