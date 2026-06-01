import _G
from _G import wait
import stage, utils, graphics, Input, position
import os
from glob import glob
import logging
import re
from datetime import datetime,timedelta
from obswebsocket import obsws
from obswebsocket import requests as obsreq

logging.basicConfig(level=logging.INFO)

def get_time():
  return utils.ocr_rect((418, 26,513, 54), 'time.png', num_only=1, color=(101, 244, 206))

def summon():
  Input.drag_to(92, 52, 819, 424, dur=0.1)

def start_dragon_fiber():
  def _deploy(poses):
    for x1, y1, x2, y2 in poses:
        Input.drag_to(x1, y1, x2, y2, hold=0.1, dur=0.1)
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
    elif not flag_battle and stage.is_stage('Battle'):
      for _ in range(5):
        yield
        wait(0.1)
      Input.rclick(1320, 35)
      for _ in range(3):
        yield
        wait(0.1)
      yield from _deploy([
        (102, 796, 767, 204),
        (1494, 815, 1378, 287),
        (84, 806, 1068, 292),
        (239, 820, 525, 344),
        (495, 804, 242, 403),
        (233, 809, 943, 568),
      ])
      for _ in range(2):
        Input.rclick(1513, 50)
        wait(0.1)
      for _ in range(60):
        yield
        wait(0.1)
      yield from _deploy([
        (942, 803, 1082, 388),
      ])
      for _ in range(80):
        yield
        wait(0.1)
      yield from _deploy([
        (512, 806, 1373, 503),
      ])
      for _ in range(80):
        yield
        wait(0.1)
      yield from _deploy([
        (639, 799, 915, 204),
      ])
      flag_battle = True
      summon_timer = datetime.now() - timedelta(seconds=10)
      support_timer = datetime.now()
    elif flag_battle:
      if datetime.now() - support_timer > timedelta(seconds=8):
        yield from _deploy([
          (104,800,539,339),
        ])
        support_timer = datetime.now()
        wait(0.3)
      if datetime.now() - summon_timer > timedelta(seconds=20):
        _G.log_info("Use summon")
        summon()
        summon_timer = datetime.now()
