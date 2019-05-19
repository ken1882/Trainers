import G, const, util
import random
from G import uwait

def random_click(x, y, rrange=G.DefaultRandRange):
  if rrange is None:
    rrange = G.DefaultRandRange
  util.click(x + random.randint(-rrange,rrange), y + random.randint(-rrange,rrange))

def delayed_click(x, y, delay, rrange=G.DefaultRandRange):
  uwait(delay)
  random_click(x, y, rrange)

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