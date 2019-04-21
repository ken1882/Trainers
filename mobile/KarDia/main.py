import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time
import const, util, action, stage, freeze
from datetime import datetime

PWD = os.path.dirname(os.path.realpath(__file__))
running = True
Hwnd    = win32gui.GetForegroundWindow()
AppHwnd = 0
FPS = (1 / 120)

LastRecoveryTime   = datetime(1970,1,1)
FlagRecoverStamina = False
FlagDebug          = False
OreLocation        = []

# Map align: topest and left:2-F4 Flag
Mode = 0
# N   | Function
# 0   | inf. grinding at 2-G4-1, if others will stop when no stamina
# 1   | Mining Grind, press CTRL and memory ore location
# other: will stop once no stamina

# First/Advanced/Completely explore
LevelDifficulty = 0

def find_bs():
  def callback(handle, data):
    global AppHwnd
    if win32gui.GetWindowText(handle) != "BlueStacks":
      return 
    rect = win32gui.GetWindowRect(handle)
    if rect[0] + rect[1] < 20:
      AppHwnd = handle
  win32gui.EnumWindows(callback, None)

def uwait(sec):
  util.wait(sec)

def update_keystate():
  global running, OreLocation
  if win32api.GetAsyncKeyState(win32con.VK_F9):
    running = False
  if Mode == 1 and win32api.GetAsyncKeyState(win32con.VK_CONTROL) and len(OreLocation) < 2:
    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON):
      pos = win32api.GetCursorPos()
      if len(OreLocation) == 1 and pos == OreLocation[0]:
        return 
      OreLocation.append(pos)
      print("Key recorded:", OreLocation)

def main_update():
  update_keystate()
  if freeze.is_frozen():
    restart_game()
    freeze.reset()

def process_recovery():
  global FlagRecoverStamina, LastRecoveryTime, running
  print("Process Recovery")

  if (datetime.now() - LastRecoveryTime).total_seconds() < 120:
    print("Recovery exhausted")
    running = False
    return

  if stage.is_stage_level() or stage.is_stage_boss():
    action.leave_level()
    uwait(1)

  if stage.is_stage_map():
    action.random_click(*const.ShopPos)
    uwait(1)
  
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
    while not stage.is_stage_map():
      uwait(1)
    action.random_click(*const.LevelPos)
    while not stage.is_stage_level():
      uwait(1)

  LastRecoveryTime = datetime.now()
  FlagRecoverStamina = False

def process_update():
  global running, FlagRecoverStamina, Mode, OreLocation
  freeze.detect_freeze()
  if FlagRecoverStamina:
    process_recovery()
  if stage.is_no_stamina():
    if Mode != 0:
      running = False
      return 
    FlagRecoverStamina = True
    uwait(1)
    action.no_stamina_ok()
  elif stage.is_stage_mine() and Mode == 1 and len(OreLocation) == 2:
    action.random_click(*OreLocation[0])
    uwait(0.8)
    action.random_click(*OreLocation[1])
    uwait(3)
    action.next()
  elif stage.is_stage_level():
    action.to_battle(LevelDifficulty)
  elif stage.has_event() or stage.is_stage_loot() or stage.is_battle_end() or stage.is_stage_levelup():
    action.next()
  elif stage.is_stage_boss():
    if stage.is_stage_no_ticket():
      print("No enough ticket")
      if Mode != 0:
        running = False
      else:
        action.leave_level()
        while not stage.is_stage_map():
          uwait(1)
        action.to_level()
        uwait(1)
    else:
      action.to_boss_battle()
  elif stage.is_stage_map():
    action.to_level()


def align_window():
  rect = win32gui.GetWindowRect(AppHwnd)
  x, y, w, h = rect
  w, h = w-x,h-y
  win32gui.MoveWindow(AppHwnd, 0, 0, w, h, 1)

def reset_window():
  rect = win32gui.GetWindowRect(AppHwnd)
  x, y, w, h = rect
  w, h = w-x,h-y
  win32gui.MoveWindow(AppHwnd, 200, 0, w, h, 1)

def restart_game():
  print("Restart")
  util.click(*const.AppClosePos)
  uwait(3)
  reset_window()
  uwait(1)
  util.click(*const.AppIconPos)
  uwait(3)
  align_window()
  while not stage.is_stage_farm():
    action.random_click(*const.AppLoginPos)
    uwait(2)
  action.random_click(*const.ToTownPos)
  uwait(2)
  action.random_click(*const.ToEventShopPos)
  while not stage.is_stage_shop():
    uwait(1)
  action.leave_shop()
  uwait(2)
  mx,my = const.EventMapScrollPos
  util.scroll_up(mx, my, const.EventMapScrolldY)
  uwait(1)
  util.scroll_right(mx, my, const.EventMapScrolldX)
  uwait(1.5)

def start():
  find_bs()
  align_window()
  global running
  inter_timer = 40
  while(running):
    uwait(FPS)
    main_update()
    if win32gui.GetForegroundWindow() == Hwnd:
      continue
    inter_timer += 1
    if inter_timer > 40:
      inter_timer = 0
      print("Scene: {}, freeze timer: {}".format(stage.get_current_stage(), freeze.get_freeze_timer()))
      freeze.detect_freeze()
      process_update()

start()
