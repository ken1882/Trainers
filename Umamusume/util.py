import _G
import os
import win32gui, win32process
from time import sleep
from random import random
import traceback

def flush():
  _G.LastFrameCount = -1
  _G.CurrentStage   = -1

def wait(sec):
  sleep(sec)

def uwait(sec):
  sleep(sec + max(random() / 2, sec * random() / 5))

def resume(fiber):
  try:
    next(fiber)
  except StopIteration:
    return False
  return True

def remove_ppl():
  os.system(f"{_G.DriverName} /installDriver")
  sleep(0.1)
  os.system(f"{_G.DriverName} /disablePPL {_G.AppPid}")
  sleep(0.1)
  os.system(f"{_G.DriverName} /uninstallDriver")

def EnumWindowCallback(hwnd, lparam):
  if win32gui.IsWindowVisible(hwnd):
    if win32gui.GetWindowText(hwnd) == _G.AppWindowName:
      _G.AppHwnd = hwnd
      _G.AppTid,_G.AppPid  = win32process.GetWindowThreadProcessId(hwnd)
      print(f"App found with HWND {hwnd} ({_G.AppWindowName}), pid={_G.AppPid}")
      update_app_rect()

def update_app_rect():
  _G.AppRect = list(win32gui.GetWindowRect(_G.AppHwnd))
  _G.AppRect[2] -= _G.AppRect[0]
  _G.AppRect[3] -= _G.AppRect[1]
  _G.AppRect = tuple(_G.AppRect)
  print(f"Rect updated: {_G.AppRect}")

def find_app_window():
  win32gui.EnumWindows(EnumWindowCallback, None)

def move_window(x=None,y=None,w=None,h=None):
  x = x if x else _G.AppRect[0]
  y = y if y else _G.AppRect[1]
  w = w if w else _G.AppRect[2]
  h = h if h else _G.AppRect[3]
  win32gui.MoveWindow(_G.AppHwnd, x, y, w, h, False)
  sleep(0.1)
  update_app_rect()

def resize_app_window():
  move_window(_G.AppRect[0], 0, _G.WindowWidth, _G.WindowHeight)
  sleep(0.1)
  update_app_rect()

def safe_execute_func(func, args=[], kwargs={}):
  try:
    return func(*args, **kwargs)
  except Exception as err:
    err_info = traceback.format_exc()
    handle_exception(err, err_info)
  return _G.MsgPipeError

def handle_exception(err, errinfo):
  _G.log_error(f"An error occured during runtime!\n{str(err)}\n{errinfo}")
  