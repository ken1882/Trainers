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
  if st is None:
    freeze_timer += 1
    if freeze_timer >= G.FreezeTimeOut:
      print("Game frozen, Abort")
      util.print_window(True, "tmp/FreezeSnapshot.png")
      G.FlagRunning = False
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
    if grind.is_battle_ready():
      action.enter_level()
    else:
      action.return_base()
  elif stage.is_stage_main_menu():
    if G.FlagRepairNeeded:
      print("Process Repair")
      G.slow_update()
      G.LaterFiber = action.repair_dolls()
    elif grind.is_battle_ready():
      action.random_click(*const.CombatMenuPos)
      uwait(2)
  elif not G.FlagGrindLevel and stage.get_current_stage() is None:
    action.autocombat_next()
  else:
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
  if G.ActionFiber:
    return update_action_fiber()

  if G.is_mode_backup():
    update_grind()
  elif G.is_mode_like():
    update_like()

  if G.LaterFiber:
    update_later_fiber()
  
