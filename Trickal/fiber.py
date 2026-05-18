import _G
from _G import rwait, wait, uwait, log_info
import Input, position, graphics, stage
from random import randint
import action, utils
import math
import win32con
from datetime import datetime, timedelta

def _is_ediable():
  uneditable_icon = (
    ((422, 240),(412, 238),),
    ((247, 215, 217),(247, 161, 167),),
  )
  return not graphics.is_pixel_match(*uneditable_icon)

def start_restaurant_fiber():
  while True:
    yield
    while not stage.is_stage('RestaurantMain'):
      yield from rwait(1.0)
    Input.rclick(625,170)
    yield from rwait(1.0)
    if not _is_ediable():
      break
    Input.rclick(366, 242)
    while not stage.is_stage('RestaurantMain'):
      yield
    Input.rclick(617, 556)
    uwait(0.5)
    # Input.rclick(195, 300)
    # uwait(0.3)
    Input.rclick(945, 695)
    yield
    while not stage.is_stage('RestaurantMain'):
      x = randint(390, 420)
      y = randint(360, 370)
      Input.mouse_down(x, y, True, False)
      uwait(0.3)
      Input.mouse_up(x, y, True, False)
      yield
      uwait(0.5)
      Input.rclick(932, 594)
      yield

def start_arena_fiber():
  ALLOW_AUTOBUY_POWER_THRESHOLD = 100_0000
  while _G.FlagWorking:
    yield
    while not stage.is_stage('ArenaMain'):
      yield from rwait(1.0)
    rows = graphics.find_object('objs/oppo_power.png')
    minn_deg = 0x7fffffff
    target = None
    for i,r in enumerate(rows):
      x, y = r
      x = int(x)
      y = int(y)
      power = 0
      dx = 200
      while not power and dx > 20:
        dx -= 10
        try:
          power = int(utils.ocr_rect((x+100, y, x+200, y+24), f"oppo_power_{i}.png", num_only=True))
        except Exception:
          power = 0
        _G.log_info(f"Opponent {i} power: {power}")
      if not power:
        raise Exception(f"Failed to read opponent {i} power")
      power_deg = math.ceil(power / 100_000)
      if power_deg < minn_deg:
        minn_deg = power_deg
        target = (x, y)
    while not stage.is_stage('ArenaPrepare'):
      Input.rclick(target[0]-100, target[1]+12)
      yield from rwait(2.0)
      if stage.is_stage('ArenaRecharge'):
        if minn_deg*100_000 > ALLOW_AUTOBUY_POWER_THRESHOLD:
          log_info(f"Opponent power {minn_deg*100_000} is above autobuy threshold, skipping")
          _G.FlagWorking = False
          return
        _G.log_info(f"Buying challenge times for opponent with power {minn_deg*100_000}")
        Input.rclick(757, 534)
    Input.rclick(1009, 677)
    while True:
      yield from rwait(1.0)
      if stage.is_stage('ArenaVictory'):
        break
      elif stage.is_stage('ArenaDefeat'):
        break
    Input.rclick(915, 677)