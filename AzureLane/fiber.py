import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import combat
import utils
import itertools
from PIL import Image

def safe_click(x, y, dur=1, **kwargs):
    times = int(dur // 0.05)
    for _ in range(times):
        wait(0.05)
        yield
    Input.rclick(x, y, **kwargs)
    for _ in range(times):
        wait(0.05)
        yield
        
def go_back():
    yield from safe_click(*position.GeneralBack)

def to_home():
    while not stage.is_stage('HomePage'):
        yield from safe_click(*position.ToHomePage)

def enhance_ships():
    row = 5
    col = 3
    mx, my = 0,0
    for _ in range(col):
        mx = position.DockSelectFirst[0]
        for _ in range(row):
            my = position.DockSelectFirst[1]
            wait(0.5)
            Input.rclick(mx,my)
            for _ in range(5):
                wait(0.3)
                yield
            epos = graphics.find_object('icon_enhance.png', 0.7)[0]
            Input.rclick(epos[0]+5, epos[1]+8)
            yield from safe_click(*position.EnhanceAutoSelect)
            if stage.is_stage('NoEnhanceMats'):
                yield from to_home()
                return
            else:
                for pos in position.EnhanceConfirms:
                    yield from safe_click(*pos)
            yield from go_back()
            mx += position.DockSelectDelta[0]
        my += position.DockSelectDelta[1]
    yield from to_home()

def start_enhance_fiber():
    yield from to_home()
    yield from safe_click(*position.HomeDock)
    yield from enhance_ships()

BattleTargetIndex = 0
TeamSwapCycle = itertools.cycle(position.TeamSwaps)
def start_stage_selection_fiber():
    global BattleTargetIndex,TeamSwapCycle
    if _G.ARGV.jndex > 0:
        for _ in range(_G.ARGV.jndex):
            _ = next(TeamSwapCycle)
        _G.ARGV.jndex = 0
    yield from to_home()
    sname = _G.ARGV.stage
    sname = 'event' if sname == 'e' else sname
    _G.log_info("Going to", sname)
    if sname == 'event':
        for pos in position.EventStageClicks:
            yield from safe_click(*pos)
    else:    
        for pos in position.GoMainQuest:
            yield from safe_click(*pos)
        for _ in range(15):
            wait(0.1)
            yield
        mpos = graphics.find_object(f"quests/{sname}.png", 0.95)[0]
        Input.rclick(*mpos)
    yield from safe_click(*position.StageChosen)
    if _G.ARGV.team_swap:
        Input.rclick(*position.SwapTeam)
        wait(0.3)
        Input.rclick(*next(TeamSwapCycle), rrange=[8,2])
        BattleTargetIndex ^= 1
        wait(1)
    if _G.ARGV.battle_swap:
        Input.rclick(*position.AutoBattleSetting)
        wait(0.3)
        Input.rclick(*position.BattleTarget[BattleTargetIndex])
        BattleTargetIndex ^= 1
        wait(0.3)
    for pos in position.StartRefights:
        yield from safe_click(*pos)

def start_refight_fiber():
    global BattleTargetIndex,TeamSwapCycle
    counter  = 0
    interval = _G.ARGV.index
    if _G.ARGV.jndex > 0:
        for _ in range(_G.ARGV.jndex):
            _ = next(TeamSwapCycle)
        _G.ARGV.jndex = 0
    if not _G.ARGV.index:
        interval = 1
    while True:
        wait(1)
        yield
        if stage.is_stage('EventRefightComplete'):
            counter += 1
            _G.log_info(f"Refight {counter}/{interval} times")
            clicks = ((496, 490),(363, 107),(829, 482),(712, 501),(660, 228),(493, 381))
            for pos in clicks:
                yield from safe_click(*pos)
            if counter >= interval:
                _G.log_info("Last run, exiting")
                break
            continue
        if stage.is_stage('RefightComplete'):
            counter += 1
            _G.log_info(f"Finished {counter}/{interval} times")
            _G.log_info(f"Wait for {_G.ARGV.wait} seconds to recover moral")
            wait(_G.ARGV.wait)
            if counter < interval:
                for _ in range(10):
                    wait(0.3)
                    yield
                Input.rclick(*position.RefightAgain)
            else:
                counter = 0
                Input.rclick(*position.RefightCancel)
                if not _G.ARGV.no_enhance:
                    yield from start_enhance_fiber()
                yield from start_stage_selection_fiber()
        elif stage.is_stage('ObtainNewShip'):
            for _ in range(2):
                yield from safe_click(*position.GeneralConfirm)
        elif stage.is_stage('DockFull'):
            exit()

def start_arena_fiber():
    times = _G.ARGV.repeats
    while times > 0:
        times -= 1
        _G.log_info(f"Starting arena, times left: {times}/{_G.ARGV.repeats}")
        while not stage.is_stage('ArenaMenu'):
            wait(0.3)
            yield
        for pos in position.ArenaSelections:
            yield from safe_click(*pos)
            p = utils.str2int(utils.ocr_rect((930, 160, 980, 180), 'opower.png', num_only=1)) or 0
            _G.log_info("Opponent power:", p)
            if p > 6000:
                break
            yield from safe_click(*position.GeneralBack)
        for pos in position.ArenaStart:
            yield from safe_click(*pos)
        while not stage.is_stage('Defeated'):
            wait(1)
            yield
        for pos in position.ArenaDefeat:
            yield from safe_click(*pos)

def determine_minigame_hidx(col):
    if col[0] > 200 and col[1] > 200:
        return 1
    if col[0] > 250:
        return 2
    if col[2] > 200:
        return 0
    return -1

def start_errand_fiber():
    scroll_pos = (
        ((972, 110), (978, 110)),
        ((972, 495), (978, 495)),
    )
    AwakenErrandDispatcher = (
        (114, 127),(249, 132),(374, 131),
    )
    while True:
        yield
        if not stage.is_stage('Errand'):
            continue
        for pos in scroll_pos[0]:
            Input.click(*pos)
            yield
        wait(1)
        _G.flush()
        graphics.flush()
        errands_doing = graphics.find_object('errand_doing.png', 0.7)
        errands_done  = graphics.find_object('errand_done.png', 0.7)
        try:
            dispatched = utils.ocr_rect((825, 22, 835, 42), 'dispatched.png', num_only=True)
            print(dispatched)
            dispatched = 4 - int(dispatched[0])
        except Exception as err:
            dispatched = len(errands_doing)
            utils.handle_exception(err)
        completed  = len(errands_done)
        _G.log_info(f"Dispatched:", dispatched)
        _G.log_info(f"Completed:", completed)
        if completed > 0:
            pos = errands_done[0]
            Input.rclick(*pos)
            wait(1)
            for _ in range(5):
                Input.rclick(50, 470)
                wait(0.8)
            wait(1)
            continue
        for _ in range(5):
            yield
            wait(0.3)
        if dispatched >= 4:
            for _ in range(550):
                yield
                wait(0.1)
            continue
        for pos in scroll_pos[1]:
            Input.click(*pos)
            yield
        availables = graphics.find_object('errand_idle.png', 0.8)
        for apos in reversed(availables):
            rect = [apos[0]+90, apos[1], apos[0]+160, apos[1]+20]
            ct = utils.ocr_rect(rect, f"errand_time.png", num_only=True)
            _G.log_info("Time needed:", ct)
            if ct.startswith('10'):
                continue
            Input.rclick(*apos)
            wait(1)
            yield
            # if graphics.find_object('awaken_errand.png', 0.8):
            #     Input.rclick(200, 279)
            #     wait(1)
            #     yield
            #     if not graphics.is_pixel_match(((609, 23),), ((248, 235, 165),)):
            #         Input.rclick(580, 29)
            #         wait(1)
            #     for pos in AwakenErrandDispatcher:
            #         if sum(graphics.get_pixel(*pos, True)) < 250:
            #             continue
            #         Input.rclick(*pos)
            #         break
            #     wait(1)
            #     yield
            #     Input.rclick(782, 526)
            #     wait(1.5)
            #     yield
            for pos in [(707, 286), (836, 290), (509, 126)]:
                Input.rclick(*pos)
                wait(1)
                yield
            for _ in range(8):
                yield
                wait(0.3)
            break
        

def start_minigame_fiber():
    while True:
        yield
        cols = []
        # print('---')
        for pos in position.MiniGameOrder:
            c = graphics.get_pixel(*pos, True)
            # print(c)
            if not any([graphics.is_color_ok(c, tc) for tc in position.MiniHameHCol]):
                break
            cols.append(c)
        if len(cols) != 5:
            continue
        for c in cols:
            i = determine_minigame_hidx(c)
            Input.rclick(*position.MiniGameHit[i])