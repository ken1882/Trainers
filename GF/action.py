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

def maxdoll_to_enhance():
  G.FlagGrindLevel = False
  random_click(*const.MaxDollToEnhancePos)

def process_autocombat_again():
  random_click(*const.AutoCombatLootNextPos)
  uwait(0.5)
  if G.FlagAutoCombat and G.AutoCombatCount != 0:
    random_click(*const.AutoCombatAgainPos)
    if G.AutoCombatCount > 0:
      G.AutoCombatCount -= 1
      print("Auto-combat count left:", G.AutoCombatCount)
  else:
    random_click(*const.AutoCombatStopPos)

def process_autocombat():
  random_click(*const.AutoCombatAgainPos)
  G.fast_update()
  uwait(1)
  util.flush_screen_cache()
  stage.flush()
  uwait(2)
  has_room = True

  while not stage.autocombat_reward_ok():
    random_click(*const.AutoCombatLootNextPos)
    if stage.is_maxdoll_reached():
      print("Max doll reached")
      has_room = False
      break
    yield
  uwait(0.5)

  if has_room:
   process_autocombat_again()
  else:
    print("No room left for auto-combat rewards")
    maxdoll_to_enhance()
    G.AutoCombatCount = -1
    uwait(1)
  
  G.slow_update()

def close_combat_setup():
  random_click(*const.CloseCombatSetupPos)

def like_friend():
  random_click(*const.VisitLikePos)

def next_friend():
  random_click(*const.NextFriendPos)

def to_combat_menu():
  random_click(*const.CombatMenuPos)

def to_repair_menu():
  random_click(*const.RepairMenuPos)

def get_repair_time():
  try:
    raw = util.read_app_text(*const.RepairTimeRect, True)
    raw = [int(i) for i in raw.split(':')]
    re = raw[0] * 3600 + raw[1] * 60 + raw[2]
  except Exception as err:
    print("An error occurred during getting repair time:", err)
    re = G.WorsetRepairTime
  return re + random.randint(5,10)

def repair_dolls():
  random_click(*const.SelectRepairPos)
  for _ in range(2):
    uwait(0.5)
    yield
  if stage.is_stage_repair():
    return
  uwait(0.5)
  for i in range(G.MaxRepair):
    random_click(*const.RepairSlotPos[i])
    uwait(0.1)
  yield
  random_click(*const.RepairStartPos)
  uwait(1)
  G.RepairOKTimestamp = get_repair_time() + G.CurTime
  random_click(*const.RepairConfirmPos)
  yield
  uwait(0.2)
  return_base()

def enter_level():
  random_click(*const.EnterLevelPos[G.GrindLevel])
  uwait(1)

def start_level():
  random_click(*const.StartCombatPos)
  uwait(1)

def deploy_troops():
  for pos in const.TeamDeployPos[G.GrindLevel]:
    random_click(*pos)
    uwait(1)
    random_click(*const.DeployConfirmPos)
    uwait(0.5)
    yield
  random_click(*const.BattleStartPos)