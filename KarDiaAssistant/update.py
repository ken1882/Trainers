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

def is_minigame_token_enough():
  return int(util.read_app_text(*const.TokenNumberPos)) > 0

def determine_continue():
  if stage.is_stage_minigames():
    return is_minigame_token_enough() 
  return True

def is_minigame():
  return G.Mode == 1 or G.Mode == 2

def update_minigame():
  in_stage = True
  if G.Mode == 1:
    in_stage = slime.update()
  elif G.Mode == 2:
    in_stage = straw.update()
  
  G.FlagRunning = (in_stage or G.FlagRepeat)
  if G.FlagRepeat and stage.is_stage_minigames():
    G.FlagRunning = determine_continue()

def process_update():
  update_freeze()
  if stage.is_stage_loot() or stage.has_event():
    action.action_next()

  if is_minigame():
    update_minigame()