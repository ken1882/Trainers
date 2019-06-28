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
  print("Process backup")
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
  if G.FlagCheckCombatResources:
    G.FlagResourcesCheckNeeded = True

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
    _re = int(util.read_app_text(*const.FastRepairItemRect, dtype='digit'))
  except Exception as err:
    print("An error occurred during getting repair time:", err)
    _re = 0
  print("Fast repair item left:", _re)
  return _re

def get_repair_time():
  try:
    raw = util.read_app_text(*const.RepairTimeRect, dtype='time')
    raw = [int(i) for i in raw.split(':')]
    _re = raw[0] * 3600 + raw[1] * 60 + raw[2]
  except Exception as err:
    print("An error occurred during getting repair time:", err)
    _re = G.WorstRepairTime
  return _re

def repair_dolls():
  while not stage.is_stage_repair():
    if stage.is_stage_main_menu():
      to_repair_menu()
      uwait(1)
    yield
  
  if G.FlagCheckCombatResources:
    yield from check_resources(False)
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
  if not G.FlagSwapTeamNeeded:
    G.superslow_update()

def enter_level():
  random_click(*const.EnterLevelPos[G.GrindLevel])
  uwait(1)

def start_level():
  G.FlagPlayerTurn = True
  random_click(*const.StartCombatPos)
  uwait(1)

def start_battle():
  mx, my = const.BattleStartPos
  random_click(mx, my+20)
  print("Start combat, next in 3 seconds")
  uwait(3.8)

def end_turn():
  mx, my = const.BattleStartPos
  random_click(mx, my+20)
  print("Turn ends")
  uwait(2)

def deploy_troops():
  for i, pos in enumerate(const.TeamDeployPos[G.GrindLevel]):
    print("Deploy Team", i)
    while not stage.is_stage_combat_map():
      yield
    px, py = pos[0], pos[1]
    rrange = 0 if pos[-1] == 'unrand' else 6
    random_click(px, py, rrange)
    while not stage.is_stage_team_selected():
      yield      
    uwait(0.5)
    if not G.FlagGrindEvent:
      if i == 0 and not stage.is_ammo_enough():
        G.FlagSupplyNeeded = True
        print("Main team has no enough ammo!")
    
    random_click(*const.DeployConfirmPos)
    uwait(0.5)
    yield

def get_ap_colors():
  ar = []
  for pos in const.ActionPointPixels:
    ar.append(util.getPixel(*pos))
  return np.array(ar)

def move_troop(level, turn):
  if turn >= len(const.TeamMovementPos[level]):
    print("Mission abort flag was set!")
    G.FlagMissionAbort = True
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
          if source[0] == -1:
            source = None
          print("Move {} -> {}".format(source, dest))
          if source:
            random_click(*source, 6)
            uwait(0.5)
          random_click(*dest, 6)
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
  G.FlagGrindEvent = False
  G.FlagGrindLevel = None
  G.FlagAutoCombat = False
  G.AutoCombatCount = -1

def supply_at(x, y):
  print("Supply at", [x, y])
  while not stage.is_stage_combat_map():
    uwait(1)
    yield
  random_click(x, y, 6)
  uwait(0.5)
  random_click(x, y, 6)
  uwait(2)
  random_click(*const.SupplyIconPos)
  yield

def supply_team(tid):
  print("Supply team", tid)
  yield from supply_at(*const.TeamDeployPos[G.GrindLevel][tid])

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
  try:
    select_slot(int(ch_idx))
  except ValueError:
    pos = util.get_image_locations(ch_idx)[0]
    print("{} found at {}".format(ch_idx, pos))
    mx, my = pos
    random_click(mx, my - 80)

def get_maingunner_index(tid):
  if tid == 0:
    idx_dict = const.EditMainGunnerIndexA  
  elif tid == 1:
    idx_dict = const.EditMainGunnerIndexB
  try:
    return idx_dict[G.GrindLevel]
  except KeyError:
    return idx_dict['default']

def swap_team():
  while not stage.is_stage_formation():
    if stage.is_stage_main_menu():
      random_click(*const.FormationMenuPos)
      uwait(1)
    yield

  if G.LastMainGunner == 0:
    formation_pos = const.FormationPosB
    ch_idx = get_maingunner_index(0)
    G.LastMainGunner = 1
  else:
    formation_pos = const.FormationPosA
    ch_idx = get_maingunner_index(1)
    G.LastMainGunner = 0
  yield from change_formation(formation_pos)
  uwait(1)
  while not stage.is_stage_formation():
    yield
  random_click(*const.EchelonSecondPos)
  uwait(1)
  yield
  for i, gidx in enumerate(ch_idx):
    random_click(*const.MainGunnerSlotPos[i])
    uwait(1.5)
    change_main_gunner(gidx)
    yield
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
  G.save_update_frequency()
  G.change_update_frequency(15, 200)
  num_left = G.RetireDollNumber
  while num_left > 0:
    random_click(*const.RetireDollPos)
    yield
    uwait(2)
    sub = min([num_left, 12])
    for i in range(sub):
      select_slot(i)
      uwait(0.5)
      yield
    num_left -= sub
    random_click(*const.RetireOKPos)
    yield
    uwait(1.5)
    random_click(*const.RetireConfirmPos)
    yield
    uwait(1)
  return_base()
  yield
  G.restore_update_frequency()
  uwait(1.5)

def close_app():
  util.click(*const.AppClosePos)

def launch_app():
  try:
    pos = util.get_image_locations("assets/title.png")[0]
    util.click(pos[0]+20, pos[1]-80)
  except IndexError:
    print("Unable to find app")

def process_reboot():
  print("Game frozen, Reboot")
  stop_combat_grinds()
  util.print_window(True, "tmp/FreezeSnapshot.png")
  G.superslow_update()
  G.LaterFiber = None
  G.ActionFiber = _reboot()

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

def select_correct_level():
  print("Process to {} moves".format(G.GrindLevel))
  moves = const.ToLevelActions[G.GrindLevel]
  for pos in moves:
    if len(pos) == 4:
      random_scroll_to(*pos)
    else:
      random_click(*pos)
    yield

def get_resources():
  return [int(util.read_app_text(*rect, dtype='digit')) or 0 for rect in const.ResourceRects]

def is_resources_enough():
  print("Resources:", G.CurrentResources)
  for cur, req in zip(G.CurrentResources, G.MinCombatResources):
    if cur < req:
      print("No enough resources for combat!")
      return False
  print("Sufficient resources")
  return True

def check_resources(rebase=True):
  while not stage.is_resources_checking_stage():
    if stage.is_stage_main_menu():
      to_repair_menu()
    yield
  G.CurrentResources = get_resources()
  G.FlagResourcesCheckNeeded = False
  if rebase:
    return_base()
    uwait(1)

def switch2app():
  util.activeWindow(G.AppHwnd)
  util.click(10, -10)

def from_selection_to_level():
  if G.FlagGrindEvent:
    random_click(*const.EventPos)
  else:
    if stage.is_correct_level_selected():
      uwait(1)
      enter_level()
    else:
      print("Incorrect level selcted!")
      G.LaterFiber = select_correct_level()

def enter_event_level():
  G.FlagPlayerTurn = True
  random_click(*const.EventLevelPos[G.GrindLevel])
  uwait(2.5)
  random_click(*const.EventLevelEnterPos)
  uwait(1)

def process_instructed_movement(level, turn):
  if turn >= len(const.EventCombatMovement[level]):
    print("Mission abort flag was set!")
    G.FlagMissionAbort = True
    return

  # For each moves of turn
  for _, movement in enumerate(const.EventCombatMovement[level][turn]):
    tag  = movement[0].lower()
    args = movement[1:] if len(movement) > 1 else []

    if tag == 'move' or tag == 'swap':
      last_ap_status = get_ap_colors()
      cur_ap_status = np.array([])
      move_succ = False
      while not move_succ:
        source, dest = args[0], args[1]
        move_team(source, dest)
        if len(args) >= 3: # Confirm move to airport
          uwait(0.8)
          random_click(*args[2])
        yield from util.wait_cont(2)
        while not stage.is_stage_combat_map():
          uwait(1)
          yield
        cur_ap_status = get_ap_colors()
        move_succ = not np.array_equal(last_ap_status, cur_ap_status) or tag == 'swap'
        print("Move result: {}".format("succeed" if move_succ else "failed"))
    elif tag == 'deploy':
      print("Deply team")
      yield from unselect()
      random_click(*args[0], 6)
      uwait(2)
      random_click(*const.DeployConfirmPos)
      uwait(1)
    elif tag == 'supply':
      yield from supply_at(*args[0])
    elif tag == 'scroll':
      random_scroll_to(*args[0])
    elif tag == 'retreat':
      yield from retreat_at(*args[0])
    elif tag == 'restart':
      print("Restart mission flag was set")
      G.FlagMissionRestart = True
      uwait(2)
    elif tag == 'abort':
      print("Abort mission flag was set")
      G.FlagMissionAbort = True
      uwait(2)
    else:
      print("Warning: unknown movement tag `{}`, args: {}".format(tag, args))
    yield

def move_team(source, dest):
  if source[0] == -1:
    source = None
  print("Move {} -> {}".format(source, dest))
  if source:
    random_click(*source, 6)
    uwait(0.5)
  random_click(*dest, 6)
  uwait(0.5)

def unselect():
  while not stage.is_stage_combat_map():
    uwait(1)
    yield
  random_click(*const.CancelTeamSelectPos)
  uwait(0.8)
  random_click(*const.CancelTeamSelectPos)
  uwait(0.5)

def retreat_at(x, y):
  print("Retreat", [x, y])
  yield from unselect()
  uwait(1)
  random_click(x, y)
  uwait(0.5)
  random_click(x, y)
  uwait(2)
  random_click(*const.RetreatPos)
  uwait(2)
  random_click(*const.RetreatConfirmPos)
  uwait(1)

def abort_mission():
  random_click(*const.AbortMissionPos)
  uwait(1)
  random_click(*const.AbortConfirmPos)
  uwait(0.5)

def restart_mission():
  random_click(*const.AbortMissionPos)
  uwait(1)
  random_click(*const.RestartConfirmPos)
  uwait(0.5)

def util_back():
  util.click(*const.BackIconPos)

def process_connection_timeout():
  print("Connection time out!")
  G.ActionFiber = None
  G.LaterFiber = None
  util.save_screenshot("tmp/ConnectionTimeoutSnapshot.png")
  stop_combat_grinds()
  util_back()
  print("Pause for 5 mins...")
  uwait(300)
  random_click(*const.LoginOKPos)
  print("Pause for 10 seconds...")
  uwait(10)