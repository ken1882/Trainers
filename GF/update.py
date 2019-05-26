import G, const, util, win32api, win32con
import stage, action, Input
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

def advance(func, *args, **kwargs):
  if G.FlagManualControl:
    if not G.ActionFiber:
      print("Press CTRL to continue...")
      G.ActionFiber = fiber_manual_action(func, *args, **kwargs)
    if G.ActionFiber and not util.resume(G.ActionFiber):
      G.ActionFiber = None
  else:
    func(*args, **kwargs)

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
  if stage.is_stage_achievement():
    uwait(2)
    action.action_next()
  elif stage.is_stage_backup_ok():
    action.process_backup()
  elif stage.is_stage_autocombat_ok():
    G.ActionFiber = action.process_autocombat()
  elif stage.is_stage_combat_setup():
    action.close_combat_setup()
    uwait(0.5)
    action.return_base()
  elif stage.is_stage_combat_selection() or stage.is_stage_enhance():
    action.return_base()
  elif stage.is_stage_profile():
    action.action_next()

def update_like():
  mx, my = const.VisitLikePos
  if stage.is_stage_like():
    action.random_click(mx, my)
    uwait(0.5)
  util.scroll_right(mx-100, my-600, const.NextFriendDelta, True, True)
  uwait(1.2)

def process_update():
  update_freeze()
  stage.update()
  if G.ActionFiber:
    print("Resume Fiber")
    if not util.resume(G.ActionFiber):
      G.ActionFiber = None
      print("Fiber finished")
    return 
  if G.is_mode_backup():
    update_grind()
  elif G.is_mode_like():
    update_like()