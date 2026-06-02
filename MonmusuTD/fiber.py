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
  Input.drag_to(92, 52, 819, 424, dur=0.1)

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
        (1493, 795, 1372, 287),
        (82, 800, 1077, 295),
        (1349, 816, 527, 347),
        (649, 807, 253, 407),
      ])
      for _ in range(2):
        Input.rclick(1513, 50)
        wait(0.1)
      for _ in range(10):
        yield
        wait(0.1)
      yield from _deploy([
        (376, 799, 1164, 578)
      ])
      for _ in range(40):
        yield
        wait(0.1)
      yield from _deploy([
        (259, 795, 942, 576)
      ])
      for _ in range(60):
        yield
        wait(0.1)
      yield from _deploy([
        (665, 795,1086, 382)
      ])
      for _ in range(70):
        yield
        wait(0.1)
      yield from _deploy([
        (532, 803, 368, 485)
      ])
      for _ in range(70):
        yield
        wait(0.1)
      yield from _deploy([
        (671, 800, 776, 218)
      ])
      flag_battle = True
      summon_timer = datetime.now() - timedelta(seconds=10)
      support_timer = datetime.now()
    elif flag_battle:
      if datetime.now() - support_timer > timedelta(seconds=8):
        yield from _deploy([
          (104,800,1135, 581),
        ])
        support_timer = datetime.now()
        wait(0.3)
      if datetime.now() - summon_timer > timedelta(seconds=20):
        _G.log_info("Use summon")
        summon()
        summon_timer = datetime.now()
