import _G
from _G import log_error,log_debug,log_info,log_warning,resume,wait,uwait
import numpy as np
import os
import win32gui, win32process
from time import sleep
from random import random
import traceback
import os.path
from difflib import SequenceMatcher

def EnumWindowCallback(hwnd, lparam):
  if win32gui.IsWindowVisible(hwnd):
    if win32gui.GetWindowText(hwnd) == _G.AppWindowName:
      _G.AppHwnd = hwnd
      _G.AppTid,_G.AppPid  = win32process.GetWindowThreadProcessId(hwnd)
      print(f"App found with HWND {hwnd} ({_G.AppWindowName}), pid={_G.AppPid}")
      update_app_rect()

def EnumChildWindowCB(hwnd, lparam):
  clsname = win32gui.GetClassName(hwnd)
  title   = win32gui.GetWindowText(hwnd)
  if title == _G.AppChildWindowName:
    if len(_G.AppChildrenHwnds) == _G.AppChildIndex:
      _G.AppChildHwnd = hwnd
      print("Target child set to", "{:x}".format(hwnd))
    print("Found child with hwnd", "{:x}".format(hwnd))
    _G.AppChildrenHwnds.append(hwnd)

def update_app_rect():
  _G.AppRect = list(win32gui.GetWindowRect(_G.AppHwnd))
  _G.AppRect[2] -= _G.AppRect[0]
  _G.AppRect[3] -= _G.AppRect[1]
  _G.AppRect = tuple(_G.AppRect)
  print(f"Rect updated: {_G.AppRect}")

def find_app_window():
  win32gui.EnumWindows(EnumWindowCallback, None)

def find_child_window():
  log_info("Child windows:")
  _G.AppChildrenHwnds = []
  win32gui.EnumChildWindows(_G.AppHwnd, EnumChildWindowCB, None)
  print("\n\n")

def move_window(x=None,y=None,w=None,h=None):
  x = x if x else _G.AppRect[0]
  y = y if y else _G.AppRect[1]
  w = w if w else _G.AppRect[2]
  h = h if h else _G.AppRect[3]
  win32gui.MoveWindow(_G.AppHwnd, x, y, w, h, False)
  sleep(0.1)
  update_app_rect()

def resize_app_window():
  update_app_rect()
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

def diff_string(a,b):
  return SequenceMatcher(None,a,b).ratio()

def isdigit(n):
  try:
    _ = int(n)
    return True
  except Exception:
    return False

def str2int(ss):
  try:
    return int("".join([n for n in ss if isdigit(n)]))
  except ValueError:
    return None

def ensure_dir_exist(path):
  path = path.split('/')
  path.pop()
  if len(path) == 0:
    return
  pwd = ""
  for dir in path:
    pwd += f"{dir}/"
    if not os.path.exists(pwd):
      os.mkdir(pwd)