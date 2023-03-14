import G, const, util, time
import random, multiprocessing
from G import uwait
from multiprocessing import freeze_support

def random_click(x, y, rrange=G.DefaultRandRange):
  if rrange is None:
    rrange = G.DefaultRandRange
  util.click(x + random.randint(-rrange,rrange), y + random.randint(-rrange,rrange))

def _dealyed_click(x, y, delay, rrange):
  time.sleep(delay)
  random_click(x, y, rrange)
  
def delayed_click(x, y, delay, rrange=G.DefaultRandRange):
  x += G.AppRect[0]
  y += G.AppRect[1]
  G.Pool.starmap(_dealyed_click, [(x, y, delay, rrange)])

def random_scroll_to(x, y, x2, y2, **kwargs):
  rrange = kwargs.get('rrange')
  rrange = G.DefaultRandRange if rrange is None else rrange
  const_x_axis = kwargs.get('const_x_axis')
  const_y_axis = kwargs.get('const_y_axis')
  if not const_x_axis:
    x += random.randint(-rrange, rrange)
    x2 += random.randint(-rrange, rrange)
  if not const_y_axis:
    y += random.randint(-rrange, rrange)
    y2 += random.randint(-rrange, rrange)
  util.scroll_to(x, y, x2, y2, **kwargs)

def action_next(rrange=G.DefaultRandRange):
  mx, my = const.ActionContinue
  random_click(mx, my, rrange)

def no_stamina_ok():
  random_click(*const.ActionNoStaminaOK)

def to_battle(difficulty=0):
  difficulty = difficulty % 3
  random_click(*const.ActionBattle[difficulty])
  uwait(0.42, False)
  random_click(*const.ActionBattle[difficulty])

def leave_level(loc=0):
  random_click(*const.LevelLeavePos)

def close_inventory():
  random_click(*const.InventoryBackPos)

def enter_level():
  random_click(*const.LevelEnterPos)