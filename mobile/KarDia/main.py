import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time, random
import const, util, action, stage, freeze
from datetime import datetime

# assign constants
const.PWD = os.path.dirname(os.path.realpath(__file__))
const.Hwnd = win32gui.GetForegroundWindow()
const.LastRecoveryTime   = datetime(1970,1,1)

# Find hwnd of bluestack
def find_bs():
  # Callback function for EnumWindows
  def callback(handle, data):
    if win32gui.GetWindowText(handle) != "BlueStacks":
      return 
    rect = win32gui.GetWindowRect(handle)
    if rect[0] + rect[1] < 20:
      const.AppHwnd = handle
  win32gui.EnumWindows(callback, None)

def uwait(sec, rand=True):
  if rand:
    sec += random.random()
    if sec > 0.5:
      sec -= (random.random() / 3)
  util.wait(sec)

def update_keystate():
  # Stop program when press F9
  if win32api.GetAsyncKeyState(win32con.VK_F9):
    const.running = False
  # Record mine ore mouse position
  if const.Mode == 1 and win32api.GetAsyncKeyState(win32con.VK_CONTROL) and len(const.OreLocation) < 2:
    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON):
      pos = win32api.GetCursorPos()
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
    const.running = False
    return
  # Leave current level
  if stage.is_stage_level() or stage.is_stage_boss():
    action.leave_level()
    uwait(1)
  # Go to shop
  if stage.is_stage_map():
    action.random_click(*const.ShopPos)
    uwait(1)
  # Shop processing
  if stage.is_stage_shop():
    action.random_click(*const.ShopKeeperPos)
    while not stage.is_stage_shoplist():
      uwait(1)
    action.purchase_item()
    while not stage.is_stage_shop():
      uwait(1)
    action.use_recovery_item()
    while not stage.is_stage_shop():
      uwait(1)
    action.leave_shop()
    uwait(1)
    while not stage.is_stage_map():
      uwait(1)
    action.to_level(const.LevelLocationID)
    while not stage.is_stage_level():
      uwait(1)
  # Go to level and keep grinding
  if const.LevelLocationID == 1:
    const.LevelDifficulty = 0
  const.LastRecoveryTime = datetime.now()
  const.FlagRecoverStamina = False

def process_update():
  freeze.detect_freeze()
  # Process stamina recovery if flag set
  if const.FlagRecoverStamina:
    process_recovery()
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
    action.next()
  # To battle
  elif stage.is_stage_level():
    action.to_battle(const.LevelDifficulty)
  # Handle the situation only need to click 'ok'
  elif stage.has_event() or stage.is_stage_levelup():
    action.next()
  elif stage.is_stage_loot() or stage.is_battle_end():
    action.next(50)
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
    action.next(100)

# Align window to left-top corner
def align_window():
  rect = win32gui.GetWindowRect(const.AppHwnd)
  x, y, w, h = rect
  w, h = w-x,h-y
  win32gui.MoveWindow(const.AppHwnd, 0, 0, w, h, 1)

# Reset window position for restarting
def reset_window():
  rect = win32gui.GetWindowRect(const.AppHwnd)
  x, y, w, h = rect
  w, h = w-x,h-y
  win32gui.MoveWindow(const.AppHwnd, 200, 0, w, h, 1)

def restart_game():
  print("Restart")
  util.click(*const.AppClosePos)
  uwait(3)
  reset_window()
  uwait(3)
  # Check the game icon position
  if not stage.is_pixel_match(const.AppIconPixel, const.AppIconColor):
    util.click(*const.AppIconPos[1])
  else:
    util.click(*const.AppIconPos[0])
  uwait(3)
  align_window()
  # Game login process
  while not stage.is_stage_farm():
    action.random_click(*const.AppLoginPos)
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

def start():
  find_bs()
  align_window()
  inter_timer = 40
  while(const.running):
    uwait(const.FPS, False)
    main_update()
    if win32gui.GetForegroundWindow() == const.Hwnd:
      continue
    inter_timer += 1
    if inter_timer > 40:
      inter_timer = 0
      print("Scene: {}, freeze timer: {}".format(stage.get_current_stage(), freeze.get_freeze_timer()))
      freeze.detect_freeze()
      process_update()

start()