import G, const, util, time, stage
import random, multiprocessing
import numpy as np
from G import uwait
from multiprocessing import freeze_support

def random_click(x, y, rrange=G.DefaultRandRange):
  if rrange is None:
    rrange = G.DefaultRandRange
  util.click(x + random.randint(-rrange,rrange), y + random.randint(-rrange,rrange))

def random_scroll_to(x, y, x2, y2, **kwargs):
  rrange = kwargs.get('rrange')
  rrange = G.DefaultRandRange if rrange is None else rrange
  x += random.randint(-rrange, rrange)
  y += random.randint(-rrange, rrange)
  x2 += random.randint(-rrange, rrange)
  y2 += random.randint(-rrange, rrange)
  util.scroll_to(x, y, x2, y2, **kwargs)

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

def autocombat_next():
  random_click(*const.AutoCombatLootNextPos)

def process_backup():
  uwait(1)
  action_next(30)
  uwait(2)
  random_click(*const.BackupAgainPos)

def return_base():
  random_click(*const.ReturnBaseIconPos)
  uwait(1.5)

def maxdoll_to_enhance():
  random_click(*const.MaxDollToEnhancePos)
  G.ActionFiber = from_enhance_to_retire()

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
  combat_next()
  yield
  combat_next()
  uwait(1)
  util.flush_screen_cache()
  stage.flush()
  has_room = True
  uwait(1)
  while not stage.autocombat_reward_ok():
    autocombat_next()
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

def combat_next():
  random_click(*const.BattleNextPos)

def get_fast_repair_item_count():
  try:
    re = int(util.read_app_text(*const.FastRepairItemRect, dtype='digit'))
  except Exception as err:
    print("An error occurred during getting repair time:", err)
    re = 0
  print("Fast repair item left:", re)
  return re

def get_repair_time():
  try:
    raw = util.read_app_text(*const.RepairTimeRect, dtype='time')
    raw = [int(i) for i in raw.split(':')]
    re = raw[0] * 3600 + raw[1] * 60 + raw[2]
  except Exception as err:
    print("An error occurred during getting repair time:", err)
    re = G.WorstRepairTime
  return re

def repair_dolls():
  while not stage.is_stage_repair():
    if stage.is_stage_main_menu():
      to_repair_menu()
      uwait(1)
    yield
  item_count = get_fast_repair_item_count()
  random_click(*const.SelectRepairPos)
  yield from util.wait_cont(1)
  if stage.is_stage_repair():
    print("Repair needn't")
    G.RepairOKTimestamp = G.CurTime
    G.FlagRepairNeeded = False
    uwait(0.5)
    return
  for i in range(G.MaxRepair):
    random_click(*const.RepairSlotPos[i])
    uwait(0.1)
  yield
  random_click(*const.RepairStartPos)
  yield from util.wait_cont(0.5)
  sec_needed = get_repair_time()
  yield from util.wait_cont(1)
  if item_count > G.StopFastRepairItemThreshold and (G.FlagFastRepair or sec_needed >= G.FastRepairThreshold):
    print("Using Fast Repair")
    random_click(*const.FastRepairPos)
    sec_needed = 0
    uwait(0.5)
  G.RepairOKTimestamp = sec_needed + G.CurTime + random.randint(5,10)
  random_click(*const.RepairConfirmPos)
  print("Repair will be done in", util.sec2readable(sec_needed))
  G.FlagRepairNeeded = False
  yield
  uwait(0.2)
  return_base()
  uwait(1)
  util.flush_screen_cache()

def enter_level():
  random_click(*const.EnterLevelPos[G.GrindLevel])
  uwait(1)

def start_level():
  G.FlagPlayerTurn = True
  random_click(*const.StartCombatPos)
  uwait(1)

def start_battle():
  random_click(*const.BattleStartPos)
  print("Start combat, next in 3 seconds")
  uwait(3.8)

def end_turn():
  random_click(*const.BattleStartPos)
  print("Turn ends")
  uwait(2)

def deploy_troops():
  for i, pos in enumerate(const.TeamDeployPos[G.GrindLevel]):
    print("Deploy Team", i)
    random_click(*pos)
    uwait(1)
    random_click(*const.DeployConfirmPos)
    uwait(0.5)
    yield

def get_ap_colors():
  ar = []
  for pos in const.ActionPointPixels:
    ar.append(util.getPixel(*pos))
  return np.array(ar)

def move_troop(level, turn):
  if turn >= len(const.TeamMovementPos):
    return

  # For each team route points
  for team_id, team_dest in enumerate(const.TeamMovementPos[level][turn]):
    G.CurrentTeamID = team_id
    for pos in team_dest:
      if len(pos) == 1:
        print("Scroll:", pos)
        random_scroll_to(*pos[0], haste=1)
      else:
        last_ap_status = get_ap_colors()
        cur_ap_status = np.array([])
        move_succ = False
        while not move_succ:
          source, dest = pos
          print("Move {} -> {}".format(source, dest))
          random_click(*source)
          uwait(0.5)
          random_click(*dest)
          yield from util.wait_cont(2)
          while not stage.is_stage_combat_map():
            uwait(1)
            yield
          cur_ap_status = get_ap_colors()
          move_succ = not np.array_equal(last_ap_status, cur_ap_status)
          print("Move result: {}".format("succeed" if move_succ else "failed"))
      yield
    print("Team {} move complete".format(team_id+1))
    uwait(0.3)
    yield
  print("Move complete")
  uwait(0.5)

def stop_combat_grinds():
  G.FlagGrindLevel = None
  G.FlagAutoCombat = False
  G.AutoCombatCount = -1

def process_doll_maxout():
  pass

def supply_team():
  print("Supply team")
  pos = const.TeamDeployPos[G.GrindLevel][1]
  random_click(*pos)
  uwait(0.3)
  random_click(*pos)
  yield
  uwait(1)
  random_click(*const.SupplyIconPos)
  uwait(1)
  yield

def change_formation(ch_pos):
  random_click(*const.FormationEditPos)
  while not stage.is_stage_formation_edit():
    uwait(1)
    yield
  random_click(*const.FormationOpenDefaultPos)
  uwait(1)
  yield
  random_click(*ch_pos)
  uwait(0.5)
  yield
  random_click(*const.FormationOKPos)
  uwait(1.5)
  yield
  if not stage.is_force_replaced_checked():
    random_click(*const.FormationForceReplacePos)
    uwait(0.5)
  random_click(*const.FormationForceReplaceOKPos)
  yield
  while not stage.is_stage_formation_edit():
    uwait(1)
    yield
  random_click(*const.FormationOKPos)

def change_main_gunner(ch_idx):
  random_click(*const.MainGunnerSlotPos)
  uwait(1.5)
  try:
    select_slot(int(ch_idx))
  except ValueError:
    pos = util.get_image_locations(ch_idx)[0]
    print("{} found at {}".format(ch_idx, pos))
    random_click(*pos)

def swap_team():
  while not stage.is_stage_formation():
    if stage.is_stage_main_menu():
      random_click(*const.FormationMenuPos)
      uwait(1)
    yield

  if G.LastMainGunner == 0:
    formation_pos = const.FormationPosB
    ch_idx = const.EditMainGunnerIndexA
    G.LastMainGunner = 1
  else:
    formation_pos = const.FormationPosA
    ch_idx = const.EditMainGunnerIndexB
    G.LastMainGunner = 0
  yield from change_formation(formation_pos)
  uwait(1)
  yield
  random_click(*const.EchelonSecondPos)
  uwait(1)
  yield
  change_main_gunner(ch_idx)
  uwait(1)
  yield
  G.FlagSwapTeamNeeded = False
  return_base()
  uwait(1)
  util.flush_screen_cache()
  G.superslow_update()

def select_slot(idx):
  sx, sy = const.SelectSlotStartPos.copy()
  sx += const.SlotNextColDeltaX * (idx % 6)
  sy += const.SlotNextRawDeltaY * (idx // 6)
  random_click(sx, sy)

def from_enhance_to_retire():
  while not stage.is_stage_enhance():
    yield
  uwait(1)
  random_click(*const.RetirePos)
  yield
  uwait(1)
  random_click(*const.RetireDollPos)
  yield
  uwait(2)
  for i in range(G.RetireDollNumber):
    select_slot(i)
    uwait(0.5)
    yield
  random_click(*const.RetireOKPos)
  yield
  uwait(1.5)
  random_click(*const.RetireConfirmPos)
  yield
  uwait(1)
  return_base()
  yield
  uwait(1.5)

def close_app():
  util.click(*const.AppClosePos)

def launch_app():
  pos = util.get_image_locations("assets/title.png")[0]
  util.click(pos[0]+20, pos[1]-80)

def process_reboot():
  print("Game frozen, Reboot")
  util.print_window(True, "tmp/FreezeSnapshot.png")
  G.LaterFiber = None
  G.ActionFiber = _reboot()
  # todo: auto adjust combat init zooms
  stop_combat_grinds()

def _reboot():
  if "BlueStacks" not in const.AppName:
    G.FlagRunning = False
    print("Unsupported engine for rebooting")
    return
  print("Reboot Engine")
  G.FlagRebooting = True
  G.AppHwnd = 0
  yield
  ori_bst_rect = util.find_tweaker()
  util.activeWindow(G.BSTHwnd)
  mx, my = const.BSTForceStopPos
  uwait(1)
  util.click(mx + G.BSTRect[0], my + G.BSTRect[1], False)
  print("Stop BS")
  G.superslow_update()
  cx, cy = const.EngineClosedPixel
  while not stage.is_color_ok(util.getWindowPixels(ori_bst_rect)[cx, cy], const.EngineClosedColor):
    yield
  mx, my = const.BSTStartBSPos
  util.click(mx + G.BSTRect[0], my + G.BSTRect[1], False)
  print("Start BS")
  while not stage.is_stage_desktop():
    if G.AppHwnd == 0:
      util.find_app()
      if G.AppHwnd > 0:
        util.align_window()
    yield
  uwait(1)
  yield