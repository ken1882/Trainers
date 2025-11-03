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
    level = 1
    while _G.FlagRunning:
        yield
        if stage.is_stage("StageSelect"):
            Input.click(1293, 743)
            yield from rwait(2.0)
            level += 1
            if _G.ARGV.letter:
                Input.click(1063, 550)
                yield
                Input.click(1349, 669)
            else:
                if level % 5 == 0:
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
                action.move_forward(0.03)
                yield from rwait(3)
                Input.move_delta(550, 0)
                state = 'running'
            elif state == 'running':
                if datetime.now() - atk_timer >= timedelta(seconds=15):
                    atk_counter += 1
                    Input.mouse_down()
                    yield from rwait(2)
                    Input.mouse_up()
                    yield from rwait(1)
                    atk_timer = datetime.now()
                    Input.trigger_key(ord('S'))
                    if atk_counter >= 2:
                        yield from rwait(1)
                        action.move_backward(0.03)
                        atk_counter -= 0.8
                elif graphics.is_pixel_match(*BossStop, True):
                    action.interact()
                    yield from rwait(1)
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
        if counter > 150:
            log_warning("Mission timeout, restarting")
            action.restart()

def start_fishing_fiber():
    depth = 0
    while _G.FlagRunning:
        yield
        if stage.is_stage("FishingReady"):
            log_info("Casting/Reeling fishing line")
            action.jump()
            yield from rwait(1.0)
            depth += 1
        elif stage.is_stage("FishingMooch"):
            log_info("Mooching fish")
            Input.trigger_key(ord('E'))
            yield from rwait(1.0)
        elif stage.is_stage("FishingReward"):
            log_info("Fishing success")
            Input.click()
            yield from rwait(2.0)
        else:
            depth = 0
        if depth > 30:
            log_info("Probably out of fish/bait, stopping")
            return