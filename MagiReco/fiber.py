import enum
from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
import combat
from utils import ocr_rect

def start_mirror_fiber():
  _n = int(_G.ARGV.repeats) or 0
  log_info('Current stage:', stage.get_current_stage())
  for cnt in range(_n):
    stg = stage.get_current_stage()
    if stg == 'MirrorPvPSelection':
      log_info("Mirroe level completed")
      break
    elif stg == 'MirrorRanking' or stg == 'MirrorLevel': 
      log_info("Select opponent")
      ar = [int(ocr_rect(rect,f'opow{i}.png',num_only=True)) for i,rect in enumerate(position.OpponentPowerRect)]
      log_info("Opponent power:", ar)
      idx = ar.index(min(ar))
      uwait(0.3)
      Input.click(*position.MirrorOpponentSelect[idx])
      for _ in range(10):
        uwait(0.05)
        yield
      uwait(0.3)
      Input.click(*position.MirrorBattleStart)
      yield from combat.start_combat()
      uwait(0.3)
      for _ in range(3):
        uwait(0.5)
        Input.click(*position.GeneralNext)
    for _ in range(10):
      uwait(0.05)
      yield

def start_combat_fiber():
  yield from combat.start_combat()