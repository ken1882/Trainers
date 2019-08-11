import G, const, util, win32api, win32con
import stage, action, Input, grind
from G import uwait

minigame_pos = [0,0]
key_cooldown = 0
freeze_timer = 0

def counter_up():
  if not G.FlagManualControl and G.FlagCounter:
    G.Counter += 1
    print("Counter:", G.Counter)

def fiber_manual_action(func, *args, **kwargs):
  while True:
    if (not G.FlagManualControl or Input.is_trigger(Input.keymap.kCONTROL)):
      func(*args, **kwargs)
      break
    yield

def update_keystate():
  global key_cooldown
  if key_cooldown > 0:
    key_cooldown -= 1
    return
  # Stop program when press F9
  if Input.is_trigger(win32con.VK_F9, False):
    G.FlagRunning = False
    key_cooldown = 10
  elif Input.is_trigger(win32con.VK_F8, False):
    G.FlagPaused ^= True
    key_cooldown = 10
    print("Paused: {}".format(G.FlagPaused))
    util.getPixel()

def main_update():
  Input.update()
  update_keystate()
  G.CurTime = util.get_current_time_sec()

def update_freeze():
  global freeze_timer
  st = stage.get_current_stage()
  if st is None or st == "Loading":
    freeze_timer += 1
    if freeze_timer >= G.FreezeTimeOut:
      curtime = util.get_current_time_sec()
      if G.FlagRebooting or curtime < G.LastFreezeTime + G.FronzenStopThershold:
        print("Totally frozen, abort")
        util.save_screenshot("tmp/TotallyFronzenSnapshot.png")
        G.FlagRunning = False
        exit()
      else:
        print("Game frozen, process reboot")
        util.save_screenshot("tmp/FirstFronzenSnapshot.png")
        G.LastFreezeTime = curtime
        action.process_reboot()
        freeze_timer = 0
  else:
    freeze_timer = 0
  print("Stage: {}, freeze timer: {}".format(st, freeze_timer))

def update_grind():
  if stage.is_in_battle() or grind.Fiber or grind.MovementFiber:
    print("Update grind")
    return grind.update()
  elif stage.is_stage_achievement():
    uwait(2)
    action.action_next()
  elif stage.is_stage_backup_ok():
    action.process_backup()
  elif stage.is_stage_autocombat_ok():
    if action.is_resources_enough():
      G.ActionFiber = action.process_autocombat()
    else:
      action.stop_combat_grinds()
  elif stage.is_stage_enhance():
    action.return_base()
  elif stage.is_stage_profile():
    action.action_next()
  elif stage.is_stage_autocombat_again():
    action.process_autocombat_again()
  elif stage.is_maxdoll_reached():
    action.maxdoll_to_enhance()
  elif stage.is_stage_combat_setup():
    if grind.is_battle_ready():
      grind.initialize()
      action.start_level()
    else:
      action.close_combat_setup()
  elif stage.is_stage_event_level_selection():
    if grind.is_battle_ready():
      grind.initialize()
      action.enter_event_level()
    else:
      action.return_base()
  elif stage.is_stage_combat_selection():
    if G.LaterFiber:
      return
    uwait(1)
    if grind.is_battle_ready():
      action.from_selection_to_level()
    else:
      action.return_base()
  elif stage.is_stage_main_menu():
    if not G.LaterFiber and G.FlagRepairNeeded:
      G.CheckRepairTimer += 1
      print("Repair cnt timer: {}/{}".format(G.CheckRepairTimer, G.CheckRepairCount))
      if G.CheckRepairTimer >= G.CheckRepairCount:
        print("Process Repair")
        G.CheckRepairTimer = 0
        G.slow_update()
        G.LaterFiber = action.repair_dolls()
        uwait(1)
      else:
        G.RepairOKTimestamp = G.CurTime
        G.FlagRepairNeeded = False
        uwait(0.5)
    elif not G.LaterFiber and G.FlagSwapTeamNeeded:
      print("Swap team")
      G.LaterFiber = action.swap_team()
      uwait(1)
    elif grind.is_battle_ready():
      if action.is_resources_enough():
        action.random_click(*const.CombatMenuPos)
        uwait(2)
      else:
        action.stop_combat_grinds()
  elif stage.is_stage_repair() and not G.FlagRepairNeeded and not G.LaterFiber:
    action.return_base()
  elif stage.is_stage_formation() and not G.FlagSwapTeamNeeded and not G.LaterFiber:
    action.return_base()
  elif stage.is_stage_reward():
    action.combat_next()
  elif G.FlagGrindLevel or G.FlagGrindEvent:
    grind.update()
  elif stage.get_current_stage() is None and not stage.is_in_battle() and not G.ActionFiber and not G.LaterFiber:
    action.autocombat_next()

def update_like():
  if stage.is_stage_like():
    action.like_friend()
    uwait(0.5)
  action.next_friend()
  uwait(1.4)

def update_action_fiber():
  print("Resume Action Fiber")
  if not util.resume(G.ActionFiber):
    G.ActionFiber = None
    print("Action Fiber finished")

def update_later_fiber():
  print("Resume Later Fiber")
  if not util.resume(G.LaterFiber):
    G.LaterFiber = None
    print("Later Fiber finished")

def process_update():
  update_freeze()
  stage.update()
  
  if stage.is_connection_timeout():
    action.process_connection_timeout()
    return

  if G.FlagRebooting:
    return update_reboot_process()
  if G.ActionFiber:
    return update_action_fiber()

  if stage.is_stage_annoucement():
    uwait(1)
    action.random_click(*const.AnnoucementOKPos)
  elif stage.is_stage_game_events():
    uwait(1)
    action.random_click(*const.GameEventOKPos)
  elif G.FlagResourcesCheckNeeded and not G.LaterFiber and (stage.is_stage_main_menu() or stage.is_resources_checking_stage()):
    G.LaterFiber = action.check_resources()
  elif G.is_mode_backup():
    update_grind()
  elif G.is_mode_like():
    update_like()
  elif stage.is_stage_desktop():
    G.FlagRebooting = True
    G.ActionFiber = None
    G.LaterFiber = None

  if G.LaterFiber:
    update_later_fiber()
  
def update_reboot_process():
  if G.ActionFiber:
    return update_action_fiber()

  if stage.is_stage_desktop():
    uwait(1)
    action.launch_app()
  elif stage.is_engine_starting():
    pass
  else:
    if stage.is_stage_main_menu():
      G.FlagRebooting = False
      return
    uwait(1)
    action.autocombat_next()
