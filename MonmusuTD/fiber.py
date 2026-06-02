import _G
from _G import wait
import stage, utils, graphics, Input, position
import os
from glob import glob
import logging
import re
from datetime import datetime,timedelta

logging.basicConfig(level=logging.INFO)

def get_time():
  return utils.ocr_rect((418, 26,513, 54), 'time.png', num_only=1, color=(101, 244, 206))

def summon():
  _G.log_info("Use summon")
  Input.drag_to(92, 52, 740, 376, dur=0.1)

def refill_summon():
  Input.rclick(111, 76)
  wait(0.8)
  Input.rclick(905, 545)

def start_dragon_fiber():
  def _deploy(poses):
    for x1, y1, x2, y2 in poses:
        Input.drag_to(x1, y1, x2, y2, hold=0.2, dur=0.1)
        yield
        wait(0.1)

  flag_battle = False
  summon_timer = datetime.now()
  support_timer = datetime.now()
  while _G.FlagWorking:
    yield
    if stage.is_stage('Finished'):
      graphics.take_snapshot(filename=f"result_{len(glob('.tmp/result_*.png'))}.png")
      for _ in range(5):
        for pos in ((1439, 785), (796,605)):
          Input.rclick(*pos)
          yield
          wait(0.3)
    elif stage.is_stage('QuestSelect'):
      Input.rclick(1290, 213)
    elif stage.is_stage('QuestInfo'):
      Input.rclick(1218, 684)
      for _ in range(10):
        yield
        wait(0.1)
      Input.rclick(1383, 782)
      flag_battle = False
    elif stage.is_stage('NetworkError'):
      Input.rclick(912, 483)
    elif not flag_battle and stage.is_stage('Battle'):
      for _ in range(5):
        yield
        wait(0.1)
      Input.rclick(1320, 35)
      for _ in range(3):
        yield
        wait(0.1)
      yield from _deploy([
        (229, 804, 570, 581),
        (1494, 801, 426, 218),
        (243, 811, 383, 470),
        (646, 804, 1368, 510),
        (517, 803, 1345, 728),
        (84, 795, 773, 204),
      ])
      for _ in range(2):
        Input.rclick(1513, 50)
        wait(0.1)
      for _ in range(15):
        yield
        wait(0.1)
      yield from _deploy([
        (390, 809, 1077, 292),
      ])
      for _ in range(40):
        yield
        wait(0.1)
      summon()
      for _ in range(30):
        yield
        wait(0.1)
      yield from _deploy([
        (664, 796, 251, 405),
      ])
      for _ in range(10):
        yield
        wait(0.1)
      yield from _deploy([
        (518, 807, 831, 652)
      ])
      wait(10)
      summon()
      wait(14)
      refill_summon()
      wait(1)
      summon()
      wait(20)
      summon()
      wait(25)
      refill_summon()
      wait(1)
      summon()
      wait(14)
      summon()
