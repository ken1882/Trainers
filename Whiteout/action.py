import _G
from _G import wait

import utils
import Input
import stage
import position

def close_all_windows():
    for _ in range(10):
        Input.click(*position.CommonBackPos)
        wait(1)
        yield
    if stage.is_stage('Profile'):
        Input.click(*position.CommonBackPos)
        wait(1)
        yield

def remove_hero(*pos):
    assigned = stage.get_assigned_hero_index()
    for i in pos:
        if i in assigned:
            Input.click(*position.RemoveHeroPos[i])
            wait(1.5)
            yield
