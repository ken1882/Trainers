import G, const, util, time, stage
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

def action_next(rrange=G.DefaultRandRange):
  mx, my = const.ActionContinue
  random_click(mx, my, rrange)

def process_backup():
  uwait(1)
  action_next(30)
  uwait(2)
  random_click(*const.BackupAgainPos)

def return_base():
  random_click(*const.ReturnBaseIconPos)

def process_autocombat():
  random_click(*const.AutoCombatAgainPos)
  origst, oriudt = G.ScreenTimeout, G.InternUpdateTime
  G.ScreenTimeout = 1000
  G.InternUpdateTime = 30
  uwait(1)
  util.flush_screen_cache()
  stage.flush()
  uwait(2)
  has_room = True

  while not stage.autocombat_reward_ok():
    random_click(*const.AutoCombatLootNextPos)
    if stage.is_maxdoll_reached():
      has_room = False
      break
    yield
  uwait(0.5)

  if has_room:
    random_click(*const.AutoCombatLootNextPos)
    uwait(0.5)
    if G.FlagAutoCombat and G.AutoCombatCount != 0:
      random_click(*const.AutoCombatAgainPos)
      if G.AutoCombatCount > 0:
        G.AutoCombatCount -= 1
        print("Auto-combat count left:", G.AutoCombatCount)
    else:
      random_click(*const.AutoCombatStopPos)
  else:
    print("No room left for auto-combat rewards")
    random_click(*const.MaxDollToEnhancePos)
    G.AutoCombatCount = -1
    uwait(1)
  
  G.ScreenTimeout, G.InternUpdateTime = origst, oriudt

def close_combat_setup():
  random_click(*const.CloseCombatSetupPos)