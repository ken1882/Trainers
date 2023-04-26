import _G
from _G import wait

import utils
import Input
import stage
import position

def close_all_windows():
    for _ in range(9):
        Input.click(*position.CommonBackPos)
        wait(1)
        yield
    wait(5)
    while stage.is_stage('Profile'):
        Input.click(*position.CommonBackPos)
        for _ in range(5):
            wait(1)
            yield

def remove_hero(*pos):
    assigned = stage.get_assigned_hero_index()
    for i in pos:
        if i in assigned:
            Input.click(*position.RemoveHeroPos[i])
            wait(1.5)
            yield

def open_map_search():
    Input.click(*position.MapSearchPos)
    wait(2)
    yield

def do_map_search(level):
    for _ in range(8):
      Input.click(*position.SearchLevelDec)
      wait(0.3)
      yield
    for _ in range(level-1):
      Input.click(*position.SearchLevelInc)
      wait(0.3)
      yield
    wait(0.5)
    Input.click(*position.MapSearchStart)
    wait(0.03)
    Input.click(*position.MapSearchStart)
    wait(2)
    yield

def goto_city():
    pass

def goto_map():
    pass
