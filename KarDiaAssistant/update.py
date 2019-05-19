import G, util, win32api, win32con, freeze, stage, const, action
import slime, straw, Input
from G import uwait

minigame_pos = [0,0]
key_cooldown = 0

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
  elif G.Mode == 1 and G.FlagManualControl and Input.is_trigger(win32con.VK_CONTROL, False):
    slime.identify(G.FlagAutoPlay)

def main_update():
  Input.update()
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
  global minigame_pos
  in_stage = True
  if stage.is_stage_minigames():
    print("Press right mouse button to record minigame position")
    if sum(minigame_pos) == 0 and Input.is_trigger(win32con.VK_RBUTTON):
      minigame_pos = win32api.GetCursorPos()
      print("Mini game position recored: ", minigame_pos)
      uwait(1)
    elif sum(minigame_pos) > 0:
      print("Entering minigame")
      action.random_click(*minigame_pos)
      uwait(0.5)
      action.random_click(*const.MiniGameEnterPos)
  else:
    if G.Mode == 1:
      in_stage = slime.update()
    elif G.Mode == 2:
      in_stage = straw.update()
  
  G.FlagRunning = (in_stage or G.FlagRepeat)
  if G.FlagRepeat and stage.is_stage_minigames():
    cont = determine_continue()
    G.FlagRunning = cont
    if cont:
      pass

def process_update():
  update_freeze()
  if stage.is_stage_loot() or stage.has_event():
    action.action_next()

  if is_minigame():
    update_minigame()