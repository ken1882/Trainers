import G, const, util, win32api, win32con
import freeze, stage, action, Input
import slime, straw, mine
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
  
  if G.is_mode_slime():
    slime.update_keystate()

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
  return int(util.read_app_text(*const.TokenNumberPos, True)) > 0

def determine_continue():
  if stage.is_stage_minigames():
    return is_minigame_token_enough() 
  return True

def is_minigame():
  return G.is_mode_slime() or G.is_mode_straw()

def update_minigame():
  global minigame_pos
  in_stage = True
  if stage.is_stage_minigames():
    if G.FlagRepeat and sum(minigame_pos) == 0:
      print("Press right mouse button to record minigame position")
      if Input.is_trigger(win32con.VK_RBUTTON):
        mx, my = win32api.GetCursorPos()
        mx, my = mx - G.AppRect[0], my - G.AppRect[1]
        minigame_pos = [mx, my]
        print("Mini game position recored: ", minigame_pos)
        uwait(1)
    if sum(minigame_pos) > 0:
      cont = determine_continue()
      if cont:
        print("Entering minigame")
        action.random_click(*minigame_pos)
        uwait(0.5)
        action.random_click(*const.MiniGameEnterPos)
      else:
        G.FlagRunning = False
        print("No token!")
  else:
    if G.is_mode_slime():
      in_stage = slime.update()
    elif G.is_mode_straw():
      in_stage = straw.update()
  
  G.FlagRunning = (in_stage or G.FlagRepeat)

def process_update():
  update_freeze()
  if stage.is_no_stamina():
    print("No Stamina!")
    G.FlagRunning = False
    return False
  elif stage.is_stage_loot() or stage.has_event() or stage.is_battle_end():
    action.action_next()
  elif stage.is_battle_ready():
    uwait(1)
    action.action_next(100)

  if is_minigame():
    update_minigame()
  else:
    print("Stage: {}, freeze timer: {}".format(stage.get_current_stage(), freeze.get_freeze_timer()))
    if G.is_mode_mine():
      mine.update()
