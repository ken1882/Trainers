import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time, random, sys
import const, util, action, stage, freeze
import numpy as np
from datetime import datetime

# assign constants
const.PWD = os.path.dirname(os.path.realpath(__file__))
const.Hwnd = win32gui.GetForegroundWindow()
const.LastRecoveryTime   = datetime(1970,1,1)
LastHwnd = None

# Find hwnd of bluestack
def find_bs():
  # Callback function for EnumWindows
  def callback(handle, data):
    if win32gui.GetWindowText(handle) != "BlueStacks":
      return 
    try:
      rect = win32gui.GetWindowRect(handle)
      x, y, w, h = rect
      w, h = w-x,h-y
      win32gui.MoveWindow(handle, x, y, w, h, 1)
      const.AppHwnd = handle
    except Exception:
      pass
  win32gui.EnumWindows(callback, None)
  getAppRect()

def uwait(sec, rand=True):
  if rand:
    sec += random.random()
    if sec > 0.5:
      sec -= (random.random() / 3)
  util.wait(sec)


LastAppRect = np.array([0,0,0,0])
def getAppRect():
  global LastAppRect
  rect = win32gui.GetWindowRect(const.AppHwnd)
  x, y, w, h = rect
  # x = max([x, 0])
  # y = max([y, 0])
  w, h = w-x, h-y
  if not np.array_equal(LastAppRect, np.array([x,y,w,h])):
    print("App changed: {}".format([x,y,w,h]))
    LastAppRect = np.array([x,y,w,h])
  const.AppRect = [x,y,w,h]
  return [x, y, w, h]

key_cooldown = 0

def update_keystate():
  global key_cooldown
  if key_cooldown > 0:
    key_cooldown -= 1
    return
  # Stop program when press F9
  if win32api.GetAsyncKeyState(win32con.VK_F9):
    const.running = False
    key_cooldown = 10
  elif win32api.GetAsyncKeyState(win32con.VK_F8):
    const.paused ^= True
    key_cooldown = 10
    print("Paused: {}".format(const.paused))

  # Record mine ore mouse position
  if const.Mode == 1 and win32api.GetAsyncKeyState(win32con.VK_CONTROL) and len(const.OreLocation) < 2:
    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON):
      pos = win32api.GetCursorPos()
      pos = [pos[0] - const.AppRect[0], pos[1] - const.AppRect[1]]
      key_cooldown = 10
      # return if record yet completed
      if len(const.OreLocation) == 1 and pos == const.OreLocation[0]:
        return 
      const.OreLocation.append(pos)
      print("Key recorded:", const.OreLocation)

def main_update():
  update_keystate()
  # Restart if game is frozen
  if freeze.is_frozen():
    restart_game()
    freeze.reset()

# Stamina recovery process
def process_recovery():
  print("Process Recovery")
  # Stop if (probably) no stamina recover item left
  if (datetime.now() - const.LastRecoveryTime).total_seconds() < 120:
    print("Recovery exhausted")
    return restart_game()
  # Leave current level
  while stage.is_stage_level() or stage.is_stage_boss() and not stage.is_stage_map():
    action.leave_level()
    uwait(1)
    yield
  # Go to shop
  while stage.is_stage_map() and not stage.is_stage_shop():
    action.random_click(*const.ShopPos)
    uwait(1)
    yield
  # Shop processing
  if stage.is_stage_shop():
    uwait(2)
    action.random_click(*const.ShopKeeperPos)
    while not stage.is_stage_shoplist():
      uwait(1)
      yield

    fiber = action.purchase_item()
    while util.resume(fiber):
      yield

    while not stage.is_stage_shop():
      uwait(1)
      yield

    fiber = action.use_recovery_item()
    while util.resume(fiber):
      yield

    while not stage.is_stage_shop():
      uwait(1)
      yield
    action.leave_shop()
    uwait(1)
    while not stage.is_stage_map():
      uwait(1)
      yield
    action.to_level(const.LevelLocationID)
    while not stage.is_stage_level():
      uwait(1)
      yield
  # Go to level and keep grinding
  if const.LevelLocationID == 1:
    const.LevelDifficulty = 0
  const.LastRecoveryTime = datetime.now()
  const.FlagRecoverStamina = False

def process_update():
  if const.Mode != 1:
    freeze.detect_freeze()
  # Process stamina recovery if flag set
  if const.FlagRecoverStamina:
    if const.ActionFiber:
      alive = util.resume(const.ActionFiber)
      if not alive:
        const.ActionFiber = None
    else:
      const.ActionFiber = process_recovery()
  elif stage.is_no_stamina():
    if const.Mode != 0:
      const.running = False
      return 
    const.FlagRecoverStamina = True
    uwait(1)
    action.no_stamina_ok()
  # Mining grind process
  elif stage.is_stage_mine() and const.Mode == 1 and len(const.OreLocation) == 2:
    action.random_click(*const.OreLocation[0])
    uwait(0.8)
    action.random_click(*const.OreLocation[1])
    uwait(3)
    action.action_next()
  # To battle
  elif stage.is_stage_level():
    action.to_battle(const.LevelDifficulty)
  # Handle the situation only need to click 'ok'
  elif stage.has_event() or stage.is_stage_levelup():
    action.action_next()
  elif stage.is_stage_loot() or stage.is_battle_end():
    action.action_next(50)
  # Boss challenge grind
  elif stage.is_stage_boss():
    # Leave if no entry ticket left
    if stage.is_stage_no_ticket():
      print("No enough ticket")
      if const.Mode != 0:
        const.running = False
      else:
        action.leave_level()
        while not stage.is_stage_map():
          uwait(1)
        action.to_level(const.LevelLocationID)
        uwait(1)
    else:
      action.to_boss_battle(const.BossDifficulty)
  # Go to level if on map
  elif stage.is_stage_map():
    action.to_level(const.LevelLocationID)
  # Skip battle waiting
  elif stage.is_stage_battle() and stage.is_pixel_match(const.BattleReadyPixel, const.BattleReadyColor):
    action.action_next(100)
    uwait(0.7)

# Align window to left-top corner
def align_window(wx=None,wy=None):
  rect = win32gui.GetWindowRect(const.AppHwnd)
  x, y, w, h = rect
  w, h = w-x,h-y
  if wx is None:
    wx = x
  if wy is None:
    wy = y
  win32gui.MoveWindow(const.AppHwnd, wx, wy, const.AppWidth, const.AppHeight, 1)
  uwait(1)
  getAppRect()

# Reset window position for restarting
def reset_window():
  rect = getAppRect()
  _, _, w, h = rect
  win32gui.MoveWindow(const.AppHwnd, 0, 0, w, h, 1)

def restart_game():
  print("Restart")
  const.FlagRecoverStamina = False
  const.ActionFiber = None
  getAppRect()
  appPos = [const.AppRect[0], const.AppRect[1]]
  uwait(0.5)
  util.click(*const.AppClosePos)
  uwait(3)
  reset_window()
  uwait(1)
  getAppRect()
  uwait(1)
  util.flush_screen_cache()
  uwait(1)
  print(stage.is_pixel_match(const.AppIconPixel, const.AppIconColor))
  # Check the game icon position
  if stage.is_pixel_match(const.AppIconPixel, const.AppIconColor):
    util.click(*const.AppIconPos[0], False)
  else:
    util.click(*const.AppIconPos[1], False)

  while getAppRect()[2] > 1000:
    uwait(3)
  uwait(2)
  align_window(*appPos)
  uwait(3)
  getAppRect()
  # Game login process
  while not stage.is_stage_loading():
    if stage.is_stage_farm():
      break
    if stage.is_stage_disconnected():
      action.random_click(*const.NoInternetOKPOS)
    action.random_click(*const.AppLoginPos)
    uwait(2)
  
  while not stage.is_stage_farm():
    uwait(2)
  uwait(1)
  action.random_click(*const.ToTownPos)
  uwait(2)
  action.random_click(*const.ToEventShopPos)
  while not stage.is_stage_shop():
    uwait(1)
  action.leave_shop()
  uwait(2)
  # Auto scroll to adjust map screen location
  mx,my = const.EventMapScrollPos
  util.scroll_up(mx, my, const.EventMapScrolldY)
  uwait(1)
  util.scroll_right(mx, my, const.EventMapScrolldX)
  uwait(1.5)
  # Set correct difficulty
  if const.LevelLocationID == 1:
    const.LevelDifficulty = 0

def start():
  global LastHwnd
  find_bs()
  align_window()
  inter_timer = const.InternUpdateTime
  while(const.running):
    uwait(const.FPS, False)
    main_update()
    cur_hwnd = win32gui.GetForegroundWindow()
    if cur_hwnd != const.AppHwnd:
      LastHwnd = cur_hwnd
      continue
    elif LastHwnd != const.AppHwnd:
      print("Switched to app, begin in 1.2 seconds")
      LastHwnd = cur_hwnd
      uwait(1.2)
    
    inter_timer += 1
    if inter_timer > const.InternUpdateTime:
      inter_timer = 0
      getAppRect()
      if not const.paused:
        print("Scene: {}, freeze timer: {}".format(stage.get_current_stage(), freeze.get_freeze_timer()))    
        freeze.detect_freeze()
        process_update()

# Pre-process
if len(sys.argv) > 1:
  for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    arg = arg.split('=')
    if arg[0] == '-d':
      i += 1
      const.LevelDifficulty = const.BossDifficulty = int(sys.argv[i])
      print("Level/Boss Difficulty set to " + sys.argv[i])
    elif arg[0] == '-m':
      i += 1
      const.Mode = int(sys.argv[i])
      print("Mode:", const.Mode)
    elif arg[0] == '--debug':
      const.FlagDebug = True
    

def test_func():
  find_bs()
  align_window()
  getAppRect()

start()
# test_func()
# align_window(0,0)
# win32api.SetCursorPos(const.UseItemAmountPos)
# restart_game()