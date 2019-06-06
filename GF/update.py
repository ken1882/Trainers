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
  if stage.is_in_battle():
    return grind.update()
  elif stage.is_stage_achievement():
    uwait(2)
    action.action_next()
  elif stage.is_stage_backup_ok():
    action.process_backup()
  elif stage.is_stage_autocombat_ok():
    G.ActionFiber = action.process_autocombat()
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
  elif stage.is_stage_combat_selection():
    if G.LaterFiber:
      return
    uwait(1)
    if grind.is_battle_ready():
      if stage.is_correct_level_selected():
        uwait(1)
        action.enter_level()
      else:
        print("Incorrect level selcted!")
        G.LaterFiber = action.select_correct_level()
    else:
      action.return_base()
  elif stage.is_stage_main_menu():
    if not G.LaterFiber and G.FlagRepairNeeded:
      print("Process Repair")
      G.slow_update()
      G.LaterFiber = action.repair_dolls()
      uwait(1)
    elif not G.LaterFiber and G.FlagSwapTeamNeeded:
      print("Swap team")
      G.LaterFiber = action.swap_team()
      uwait(1)
    elif grind.is_battle_ready():
      action.random_click(*const.CombatMenuPos)
      uwait(2)
  elif not G.FlagGrindLevel and stage.get_current_stage() is None:
    action.autocombat_next()
  elif stage.is_stage_repair() and not G.FlagRepairNeeded and not G.LaterFiber:
    action.return_base()
  elif stage.is_stage_formation() and not G.FlagSwapTeamNeeded and not G.LaterFiber:
    action.return_base()
  elif stage.is_stage_reward():
    action.combat_next()
  elif G.FlagGrindLevel:
    grind.update()

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
    pass # todo

  if G.FlagRebooting:
    return update_reboot_process()
  if G.ActionFiber:
    return update_action_fiber()

  if stage.is_stage_annoucement():
    uwait(1)
    action.random_click(*const.AnnoucementOKPos[0])
    uwait(1.5)
    action.random_click(*const.AnnoucementOKPos[1])
    uwait(1.5)
    action.random_click(*const.AnnoucementOKPos[1])
    uwait(1)
  elif G.is_mode_backup():
    update_grind()
  elif G.is_mode_like():
    update_like()

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