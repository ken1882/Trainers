import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, rwait, uwait, log_info, log_warning
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import utils
import action
from PIL import Image

def start_infinite_fiber():
    while _G.FlagRunning:
        yield
        if stage.is_stage("StageSelect"):
            Input.click(1293, 743)
            yield from rwait(2.0)
            if _G.ARGV.letter:
                Input.click(1063, 550)
                yield
                Input.click(1349, 669)
            else:
                Input.click(780, 613)
                yield
                Input.click(979, 726)
            yield from rwait(2.0)
        elif stage.is_stage("RewardSelect"):
            Input.click(965, 900)
            yield from rwait(3.0)
        Input.click()
        yield from rwait(0.5)

def start_escorter_fiber():
    state = 'init'
    counter = 0
    timer = datetime.now()
    atk_timer = datetime.now()
    atk_counter = 0
    BossStop = (
        ((1070, 70),(1117, 539),(935, 34),),
        ((255, 222, 158),(0, 0, 0),(255, 0, 0),)
    )
    while _G.FlagRunning:
        yield
        if stage.is_stage("StageMap"):
            if state == 'init':
                counter = 0
                atk_counter = 0
                yield from rwait(3.0)
                Input.key_down(ord('W'))
                yield from rwait(3.0)
                action.jump()
                yield from rwait(0.3)
                Input.key_up(ord('W'))
                yield from rwait(1)
                action.interact()
                state = 'running'
            elif state == 'running':
                if graphics.is_pixel_match(*BossStop, True):
                    if atk_counter < 2 and datetime.now() - atk_timer >= timedelta(seconds=5):
                        log_info("Boss stop, attacking")
                        atk_counter += 1
                        yield from rwait(2)
                        Input.click()
                        yield from rwait(1)
                        atk_timer = datetime.now()
                    elif datetime.now() - timer >= timedelta(seconds=6):
                        Input.trigger_key(ord('E'))
                        timer = datetime.now()
                    action.interact()
                elif datetime.now() - timer >= timedelta(seconds=6):
                    Input.trigger_key(ord('E'))
                    timer = datetime.now()
        elif stage.is_stage("MissionComplete"):
            log_info(f"Mission complete, ticked: {counter}")
            state = 'init'
            counter = 0
            yield from rwait(2.0)
            Input.click(1388, 955)
            yield from rwait(1.0)
            if _G.ARGV.letter:
                Input.click(1063, 550)
                yield
                Input.click(1500, 669)
            else:
                # Input.click(780, 613)
                # yield
                Input.click(979, 726)
            yield from rwait(5.0)
        elif stage.is_stage("RewardSelect"):
            Input.click(965, 900)
            yield from rwait(3.0)
        yield from rwait(1.0)
        counter += 1
        if counter > 180:
            log_warning("Mission timeout, restarting")
            action.restart()
