import _G
from _G import log_error,log_debug,log_info,log_warning,resume,wait,uwait
import numpy as np
import os
import win32gui, win32process, win32console
from time import sleep
from random import random
import traceback
import os.path
from PIL import Image
import graphics
from difflib import SequenceMatcher

try:
  import pytesseract
except Exception:
  log_warning("Pytesseract not available, OCRs won't be available")

def EnumWindowCallback(hwnd, lparam):
  if win32gui.IsWindowVisible(hwnd):
    title = win32gui.GetWindowText(hwnd)
    if title == _G.AppWindowName:
      _G.AppHwnd = hwnd
      _G.AppTid,_G.AppPid  = win32process.GetWindowThreadProcessId(hwnd)
      print(f"App found with HWND {hwnd} ({_G.AppWindowName}), pid={_G.AppPid}")
      update_app_rect()

def EnumChildWindowCB(hwnd, lparam):
  clsname = win32gui.GetClassName(hwnd)
  title   = win32gui.GetWindowText(hwnd)
  print(hwnd, clsname, title)
  if title == _G.AppChildWindowName:
    _G.AppChildHwnd = hwnd
    print("Target child found")
    return False

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

def img2str(image_file, lang='jpn', config='--psm 12 --psm 13'):
  if not os.path.exists(image_file) and not image_file.startswith(_G.DCTmpFolder):
    image_file = f"{_G.DCTmpFolder}/{image_file}"
  return pytesseract.image_to_string(image_file, lang=lang, config=config) or ''

def ocr_rect(rect, fname, zoom=1.0, lang='jpn', config='--psm 12 --psm 13', **kwargs):
  log_info(f"Processing OCR for {fname}")
  if kwargs.get('num_only'):
    lang = 'eng'
    config += ' -c tessedit_char_whitelist=1234567890'
  elif kwargs.get('whitelist'):
    lang = 'eng'
    config += f" -c tessedit_char_whitelist={kwargs.get('whitelist')}"
  if not os.path.exists(fname):
    fname = f"{_G.DCTmpFolder}/{fname}"
  img = graphics.take_snapshot(rect, fname)
  if zoom != 1.0:
    size = (int(img.size[0]*zoom), int(img.size[1]*zoom))
    graphics.resize_image(size, fname, fname)
  bin_colors = kwargs.get('binarization_colors')
  tolerance = kwargs.get('bias_tolerance', 15)
  img.close()
  if bin_colors:
    img = Image.open(fname)
    img = img.convert('RGB')
    a = np.array(img)
    # Convert matched colors to white (255, 255, 255), everything else to black (0, 0, 0)
    mask = np.zeros_like(a[..., 0], dtype=bool)
    for color in bin_colors:
      mask |= (
          (a[..., 0] >= color[0] - tolerance) & (a[..., 0] <= color[0] + tolerance) &
          (a[..., 1] >= color[1] - tolerance) & (a[..., 1] <= color[1] + tolerance) &
          (a[..., 2] >= color[2] - tolerance) & (a[..., 2] <= color[2] + tolerance)
      )
    a[~mask] = [0, 0, 0]  # Set unmatched pixels to black
    a[mask]  = [255, 255, 255]  # Set matched pixels to white
    img = Image.fromarray(a)
    img.save(fname)
    if kwargs.get('trim'):
      PADDING = 2
      a2 = np.where(mask, 255, 0).astype(np.uint8)
      nonzero_cols = np.argwhere(a2.max(axis=0) > 0)
      left_col = nonzero_cols.min()
      right_col = nonzero_cols.max()
      bbox = (left_col - PADDING, 0, right_col + 1 + PADDING, a2.shape[0])
      cropped_img = img.crop(bbox)
      cropped_img.save(fname)
    img.close()
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

def EnumWindowSelfCB(hwnd, lparam):
  _G.SelfPid = win32process.GetCurrentProcessId()
  if win32process.GetWindowThreadProcessId(hwnd) == _G.SelfPid:
    _G.SelfHwnd = hwnd
    return False
  return True

def get_self_hwnd():
  if _G.IS_WIN32:
    _G.SelfHwnd = win32console.GetConsoleWindow()
    if _G.SelfHwnd == 0:
      win32gui.EnumWindows(EnumWindowSelfCB, None)
    return _G.SelfHwnd

def is_focused():
  if _G.IS_WIN32:
    hwnd = win32gui.GetForegroundWindow()
    return hwnd == _G.SelfHwnd or hwnd == _G.AppHwnd
  return True

def str2float(ss):
  try:
    a = ''
    for c in ss:
      if c == '.' and a and '.' not in a:
        a += c
      elif c in '0123456789':
        a += c
    return float(a)
  except Exception:
    return None