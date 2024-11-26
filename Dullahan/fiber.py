import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, rwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import action
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

def start_restart_fiber():
    yield from action.restart_bs()

def start_ad_chest_fiber():
    while True:
        graphics.flush()
        a = graphics.find_object('assets/ad_reward.png')
        if a:
            Input.click(*a[0])
            for _ in range(2):
                yield from rwait(2)
                Input.rclick(*position.AD_REWARD_CLAIM)
            yield from rwait(60) # cooldown
        yield

def start_tavern_fiber():
    TARGET_DRAW_REWARD_RANK = 2 # one point 6
    _G.log_info("Processing tavern daily")
    yield from action.back_to_main()
    while not stage.is_stage('TavernMain'):
        Input.rclick(*position.MICON_TAVERN)
        yield from rwait(3)
    _G.log_info("Processing tavern music play")
    while not stage.is_stage('TavernPlay'):
        Input.rclick(*position.TAVERN_PLAY)
        yield from rwait(3)
    for pos in position.MUSIC_REWARD_ORDER:
        Input.rclick(*pos)
        yield from rwait(1)
    while not stage.is_stage('TavernMain'):
        Input.rclick(*position.TAVERN_PLAY_CLOSE)
        yield from rwait(3)
    _G.log_info("Processing tavern draw")
    while not stage.is_stage('TavernDraw'):
        Input.rclick(*position.TAVERN_DRAW)
        yield from rwait(3)
    Input.rclick(*position.TAVERN_DRAW_FIRST)
    depth = 0
    while True:
        yield from rwait(5)
        depth += 1
        for i, pos in enumerate(position.TAVERN_DRAW_REWARD_POS):
            color = graphics.get_pixel(*pos, sync=1)
            if graphics.is_color_ok(color, position.TAVERN_DRAW_REWARD_COLOR):
                _G.log_info(f"Reward rank: {i}")
                if i >= TARGET_DRAW_REWARD_RANK:
                    _G.log_info(f"Claim reward")
                    Input.rclick(*position.TAVERN_DRAW_CLAIM)
                    break
        else:
            if depth >= 3:
                _G.log_info(f"No more redraws")
                Input.rclick(*position.TAVERN_DRAW_CLAIM)
                break
            else:
                _G.log_info(f"Redraw")
                Input.rclick(*position.TAVERN_DRAW_RE)
                break
    yield from rwait(5)
    _G.log_info("Processing tavern sign in")
    while not stage.is_stage('TavernMain'):
        Input.rclick(*position.TAVERN_DRAW_CLOSE)
        yield from rwait(3)
    while not stage.is_stage('TavernSign'):
        Input.rclick(*position.TAVERN_SIGN)
        yield from rwait(3)
    Input.rclick(*position.TAVERN_SIGN_CHECK)
    yield from rwait(3)
    while not stage.is_stage('TavernMain'):
        Input.rclick(*position.TAVERN_SIGN_CLOSE)
        yield from rwait(3)
    yield from action.back_to_main()

def start_protagonist_arena_fiber():
    yield from action.back_to_main()
    OPPONENT_INDEX = 1
    while not stage.is_stage('ArenaSelection'):
        Input.rclick(*position.MICON_ARENA)
        yield from rwait(3)
    while not stage.is_stage('ArenaProtPage'):
        Input.rclick(*position.ARENA_SELECT_PROT)
        yield from rwait(3)
    while not stage.is_stage('ArenaProtSelection'):
        Input.rclick(*position.ARENA_MAIN_ENTER)
        yield from rwait(3)
    for i in range(4):
        _G.log_info(f"Start arena #{i}")
        while stage.is_stage('ArenaProtSelection'):
            Input.rclick(*position.ARENA_MAIN_OPPONENT_LIST[OPPONENT_INDEX])
            yield from rwait(3)
        while not stage.is_stage('MatchVictory') and not stage.is_stage('MatchDefeat'):
            yield from rwait(3)
        _G.log_info("Match ended")
        while stage.is_stage('MatchVictory') or stage.is_stage('MatchDefeat'):
            Input.rclick(*position.MATCH_END_CONFIRM)
            yield from rwait(3)
        while not stage.is_stage('ArenaProtSelection'):
            yield from rwait(3)
    _G.log_info("Claim arena rewards")
    while not stage.is_stage('ArenaProtPage'):
        Input.rclick(*position.ARENA_MAIN_CLOSE_LIST)
        yield from rwait(3)
    for pos in position.ARENA_MAIN_REWARD_POS_LIST:
        for _ in range(3):
            Input.rclick(*pos)
            yield from rwait(3)
    yield from action.back_to_main()

def start_companion_arena_fiber():
    yield from action.back_to_main()
    while not stage.is_stage('ArenaSelection'):
        Input.rclick(*position.MICON_ARENA)
        yield from rwait(3)
    while not stage.is_stage('ArenaCompPage'):
        Input.rclick(*position.ARENA_SELECT_COMPANION)
        yield from rwait(3)
    while not stage.is_stage('ArenaCompSelection'):
        Input.rclick(*position.ARENA_MAIN_ENTER)
        yield from rwait(3)
    for i in range(4):
        _G.log_info(f"Start companion arena #{i}")
        while stage.is_stage('ArenaCompSelection'):
            Input.rclick(*position.ARENA_COMP_START)
            yield from rwait(5)
        while not stage.is_stage('MatchVictory') and not stage.is_stage('MatchDefeat'):
            yield from rwait(3)
        _G.log_info("Match ended")
        while stage.is_stage('MatchVictory') or stage.is_stage('MatchDefeat'):
            Input.rclick(*position.MATCH_END_CONFIRM)
            yield from rwait(3)
        while not stage.is_stage('ArenaCompSelection'):
            yield from rwait(3)
    _G.log_info("Claim arena rewards")
    while not stage.is_stage('ArenaCompPage'):
        Input.rclick(*position.ARENA_COMP_CLOSE)
        yield from rwait(3)
    for pos in position.ARENA_MAIN_REWARD_POS_LIST:
        for _ in range(3):
            Input.rclick(*pos)
            yield from rwait(3)
    yield from action.back_to_main()

def start_abyss_arena_fiber():
    yield from action.back_to_main()

def start_daily_dungeons_fiber():
    yield from action.back_to_main()
    while not stage.is_stage('DungeonsMenu'):
        Input.rclick(*position.MENU_MAIN_DUNGEON)
        yield from rwait(3)
    for pos in position.DUNGEON_SWEEP_POS_LIST:
        Input.rclick(*pos)
        yield from rwait(2)

def start_daily_rewards_fiber():
    yield from action.back_to_main()
    # free shop items
    while not stage.is_stage('ShopMenus'):
        Input.rclick(*position.MENU_MAIN_SHOP)
        yield from rwait(3)
    for pos in position.DAILY_REWARDS_POS_LIST:
        for _ in range(3):
            Input.rclick(*pos)
            yield from rwait(3)
    while not stage.is_stage('ExtraMenus'):
        Input.rclick(*position.EXTRA_MENU)
        yield from rwait(3)
    # stage skip rewards
    Input.rclick(*position.STAGE_TIME_ACCELERATE)
    yield from rwait(3)
    for _ in range(12):
        Input.rclick(*position.STAGE_TIME_ACCELERATE_OK)
        yield from rwait(1)
    for _ in range(5):
        Input.rclick(*position.STAGE_TIME_ACCELERATE_CLOSE)
        yield from rwait(1)
    # daily stage ranking rewards
    while not stage.is_stage('LeaderBoard'):
        Input.rclick(*position.MICON_LEADERBOARD)
        yield from rwait(3)
    for _ in range(5):
        Input.rclick(*position.LEADERBOARD_REWARD)
        yield from rwait(2)
    for _ in range(5):
        Input.rclick(*position.LEADERBOARD_REWARD_CLAIM)
        yield from rwait(2)
    yield from action.back_to_main()
    # daily summons
    while not stage.is_stage('SummonMenus'):
        Input.rclick(*position.MENU_MAIN_SUMMON)
        yield from rwait(3)
    for pos in position.SUMMON_REWARDS_POS_LIST:
        for _ in range(3):
            Input.rclick(*pos)
            yield from rwait(2)
    for _ in range(3):
        Input.rclick(*position.SUMMON_WEAPON_10)
        yield from rwait(5)
    Input.click(*position.BS_BACK)
    yield from rwait(3)
    for _ in range(3):
        Input.rclick(*position.SUMMON_ARMOR_10)
        yield from rwait(5)
    yield from action.back_to_main()

def start_awaken_upgrade_fiber():
    yield from action.back_to_main()

def start_companion_gift_fiber():
    yield from action.back_to_main()

def start_daily_mission_fiber():
    yield from action.back_to_main()
    while not stage.is_stage('BackpackMenu'):
        Input.rclick(*position.MENU_MAIN_BACKPACK)
        yield from rwait(3)
    for pos in position.DAILY_SYNTHESIS_POS_LIST:
        for _ in range(3):
            Input.rclick(*pos)
            yield from rwait(2)
    yield from action.back_to_main()
    _G.log_info("Open chests")
    while not stage.is_stage('ChestOpen'):
        Input.rclick(*position.CHEST_OPEN_ENTER)
        yield from rwait(3)
    _G.log_info("Disable continious open")
    for _ in range(3):
        color = graphics.get_pixel(*position.CHEST_OPEN_CONTINIOUS, sync=1)
        if graphics.is_color_ok(color, position.CHEST_OPEN_CONTINIOUS_COLOR):
            Input.rclick(*position.CHEST_OPEN_CONTINIOUS)
        yield from rwait(2)
    _G.log_info("Open chest")
    for _ in range(3):
        Input.rclick(*position.CHEST_OPEN_CLAIM)
        yield from rwait(2)
    yield from action.back_to_main()
    while not stage.is_stage('ExtraMenus'):
        Input.rclick(*position.EXTRA_MENU)
        yield from rwait(3)
    for pos in position.CLAIM_DAILY_MISSION_POS_LIST:
        for _ in range(3):
            Input.rclick(*pos)
            yield from rwait(2)


def start_routtle_fiber():
    yield from start_restart_fiber()
    yield from start_tavern_fiber()
    yield from start_daily_rewards_fiber()
    yield from start_protagonist_arena_fiber()
    yield from start_companion_arena_fiber()
    yield from start_daily_mission_fiber()

