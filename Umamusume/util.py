import pytesseract
import _G
from _G import log_error,log_debug,log_info,log_warning,resume,wait,uwait
import numpy as np
import os
import win32gui, win32process
from time import sleep
from random import random
import traceback
import os.path
from PIL import Image
import graphics
from difflib import SequenceMatcher

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

def img2str(image_file, lang='jpn', config='--psm 12 --psm 13'):
  if not os.path.exists(image_file) and not image_file.startswith(_G.DCTmpFolder):
    image_file = f"{_G.DCTmpFolder}/{image_file}"
  return pytesseract.image_to_string(image_file, lang=lang, config=config) or ''

def ocr_rect(rect, fname, zoom=1.0, lang='jpn', config='--psm 12 --psm 13'):
  log_info(f"Processing OCR for {fname}")
  if not os.path.exists(fname):
    fname = f"{_G.DCTmpFolder}/{fname}"
  img = graphics.take_snapshot(rect, fname)
  if zoom != 1.0:
    size = (int(img.size[0]*zoom), int(img.size[1]*zoom))
    graphics.resize_image(size, fname, fname)
  sleep(0.3)
  return img2str(fname, lang, config).translate(str.maketrans('。',' ')).strip()

def diff_string(a,b):
  return SequenceMatcher(None,a,b).ratio()

def isdigit(n):
  try:
    _ = int(n)
    return True
  except Exception:
    return False