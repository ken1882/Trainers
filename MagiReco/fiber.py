from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait
import Input, position, graphics
from random import randint
import combat

def start_mirror_fiber():
  _n = int(_G.ARGV.repeats) or 0
  for cnt in range(_n):
    stg = stage.get_current_stage()
    if stg == 'MirrorPvPSelection':
      break
    elif stg == 'MirrorRanking' or stg == 'MirrorLevel':
      mx,my = position.MirrorOpponentSelect
      Input.moveto(mx+randint(-10,10), my+randint(-10,10))
      uwait(0.3)
      Input.click()
      for _ in range(10):
        uwait(0.05)
        yield
      mx,my = position.MirrorBattleStart
      Input.moveto(mx+randint(-10,10), my+randint(-10,10))
      uwait(0.3)
      Input.click()
      yield from combat.start_combat()