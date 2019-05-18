import G, util, win32api, win32con, freeze, stage, const, action
import slime, straw
from G import uwait

key_cooldown = 0

def update_keystate():
  global key_cooldown
  if key_cooldown > 0:
    key_cooldown -= 1
    return
  # Stop program when press F9
  if win32api.GetAsyncKeyState(win32con.VK_F9):
    G.FlagRunning = False
    key_cooldown = 10
  elif win32api.GetAsyncKeyState(win32con.VK_F8):
    G.FlagPaused ^= True
    key_cooldown = 10
    print("Paused: {}".format(G.FlagPaused))
  elif G.Mode == 1 and G.FlagManualControl and win32api.GetAsyncKeyState(win32con.VK_CONTROL):
    slime.identify()

def main_update():
  update_keystate()
  # Restart if game is frozen
  if freeze.is_frozen():
    G.FlagRunning = False
    freeze.reset()

def update_freeze():
  # freeze.detect_freeze()
  pass

def process_update():
  # print("Scene: {}, freeze timer: {} ({})".format(stage.get_current_stage(), freeze.get_freeze_timer(), freeze.is_frozen()))    
  update_freeze()
  if stage.is_stage_slime():
    G.Mode = 1
    action.random_click(*const.SlimeOKPos)
  elif G.Mode == 1 and not G.FlagManualControl:
    slime.identify()
  elif G.Mode == 2:
    if straw.is_stage_prepare():
      action.random_click(*const.StrawReadyPos)
      uwait(2)
    elif straw.is_game_over():
      print("Game over")
      action.random_click(*const.StrawOverOKPos)
      G.FlagRunning = False
    elif straw.is_stage_game():
      straw.determine_jump()