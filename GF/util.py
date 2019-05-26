import win32api, win32gui, win32ui, win32con, const
import PIL.ImageGrab, time, random, math, G
import numpy as np
from G import uwait, wait
from PIL import Image
from PIL import ImageGrab
from ctypes import windll
from datetime import datetime
from os import system
import pytesseract as pyte

ScrollTime  = 0.03
ScrollDelta = [3,8]
Initialized = False
LastAppRect = np.array([0,0,0,0])
LastFrameCount = -1

def initialize():
  if G.AppHwnd == 0:
    raise Exception("Invalid Hwnd")
  Initialized  = True

def change_title(nt):
  system("title " + nt)

def print_window(saveimg=False, filename=G.ScreenImageFile):
  im = ImageGrab.grab(getAppRect(True))
  try:
    if G.is_mode_slime() or saveimg:
      im.save(filename)
  except Exception:
    pass
  pixels = im.load()
  return pixels

def save_screenshot(outname):
  im = ImageGrab.grab(getAppRect(True))
  ext = outname.split('.')[-1].upper()
  try:
    im.save(outname, ext)
  except Exception as err:
    print("Screenshot save failed", err, sep='\n')

def save_png(img, filename):
  try:
    img.save(filename, "PNG")
  except Exception as err:
    print("Image save failed", err, sep='\n')

# Program clean ups
def terminate():
  if G.Pool:
    G.Pool.close()
    G.Pool.terminate()

def hash_timenow():
  return datetime.now().second * 1000 + datetime.now().microsecond // 1000

ScreenSnapShot = [hash_timenow(), PIL.ImageGrab.grab().load()]

def getPixel(x=None, y=None):
  global LastFrameCount
  if LastFrameCount != G.FrameCount:
    LastFrameCount = G.FrameCount
    stamp = hash_timenow()
    if abs(ScreenSnapShot[0] - stamp) > G.ScreenTimeout:
      ScreenSnapShot[0] = stamp
      ScreenSnapShot[1] = print_window()
  if x and y:
    offset = const.getAppOffset()
    x += offset[0]
    y += offset[1]
    return ScreenSnapShot[1][x, y]
  return ScreenSnapShot[1]

def flush_screen_cache():
  global ScreenSnapShot, LastFrameCount
  ScreenSnapShot[0] = 0
  LastFrameCount = -1

def choose_best_hwnd(names, target):
  if not names:
    return -1
  if len(names) == 1:
    return 0
  else:
    if names[0][0] == target and names[1][0] != target:
      return 0
    else:
      print("Process List:")
      for idx, info in enumerate(names):
        print("[{}] ({}) {}".format(idx, info[1], info[0]))
      return input("Please choose the id of target process(-1 for abort): ")
def find_app():
  possibles = []
  target_cnt = {k:0 for k in const.TargetApps}
  # Callback function for EnumWindows
  def callback(handle, data):
    nonlocal possibles, target_cnt
    for name in const.TargetApps:
      title = win32gui.GetWindowText(handle)
      if name not in title:
        continue
      try:
        rect = win32gui.GetWindowRect(handle)
        x, y, w, h = rect
        w, h = w-x,h-y
        win32gui.MoveWindow(handle, x, y, w, h, 1)
        possibles.append([title, handle])
        target_cnt[name] += 1
      except Exception:
        pass
  win32gui.EnumWindows(callback, None)
  print(target_cnt)
  target_app = max(target_cnt, key=(lambda k:target_cnt[k]))
  print(possibles, target_app)
  possibles.sort(key=lambda ss: len(ss[0])-len(target_app)+ss[0].index(target_app))
  if possibles:
    pid = choose_best_hwnd(possibles, target_app)
    print(pid, possibles[pid][1])
    if pid >= 0:
      const.AppName = target_app
      G.AppHwnd = possibles[pid][1]
  
  if G.AppHwnd == 0:
    print("Unable to find app window, aborting")
    exit()
  else:
    print("Current App:", const.AppName)
    getAppRect()
  

# ori: return original 4 pos of the window
def getAppRect(ori=False):
  global LastAppRect
  rect = win32gui.GetWindowRect(G.AppHwnd)
  x, y, w, h = rect
  if not ori:
    w, h = w-x, h-y
    G.AppRect = [x,y,w,h]
    if not np.array_equal(LastAppRect, np.array([x,y,w,h])):
      print("App changed: {}".format([x,y,w,h]))
      LastAppRect = np.array([x,y,w,h])
  return [x, y, w, h]

# Align window to left-top corner
def align_window(wx=None,wy=None):
  rect = win32gui.GetWindowRect(G.AppHwnd)
  x, y, w, h = rect
  w, h = w-x,h-y
  if wx is None:
    wx = x
  if wy is None:
    wy = y
  ww, wh = const.getAppResoultion()
  win32gui.MoveWindow(G.AppHwnd, wx, wy, ww, wh, 1)
  uwait(1)
  getAppRect()

# Reset window position for restarting
def reset_window():
  rect = getAppRect()
  _, _, w, h = rect
  win32gui.MoveWindow(G.AppHwnd, 0, 0, w, h, 1)

def mouse_down(x, y, app_offset):
  if app_offset:
    offset = const.getAppOffset()
    x += G.AppRect[0] + offset[0]
    y += G.AppRect[1] + offset[1]
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

def mouse_up(x, y, app_offset):
  if app_offset:
    offset = const.getAppOffset()
    x += G.AppRect[0] + offset[0]
    y += G.AppRect[1] + offset[1]
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def set_cursor_pos(x, y, app_offset):
  if app_offset:
    offset = const.getAppOffset()
    x += G.AppRect[0] + offset[0]
    y += G.AppRect[1] + offset[1]
  win32api.SetCursorPos((x,y))

def click(x, y, app_offset=True):
  set_cursor_pos(x, y, app_offset)
  mouse_down(x, y, app_offset)
  mouse_up(x, y, app_offset)

def scroll_up(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  ty = y + delta
  wait(0.01 if haste else 0.5)
  while y <= ty:
    y += random.randint(*ScrollDelta)
    set_cursor_pos(x, min([y,ty]), app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_down(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  ty = y - delta
  wait(0.01 if haste else 0.5)
  while y >= ty:
    y -= random.randint(*ScrollDelta)
    set_cursor_pos(x, max([y,ty]), app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_left(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  tx = x + delta
  wait(0.01 if haste else 0.5)
  while x <= tx:
    x += random.randint(*ScrollDelta)
    set_cursor_pos(min([x,tx]), y, app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_right(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  tx = x - delta
  wait(0.01 if haste else 0.5)
  while x >= tx:
    x -= random.randint(*ScrollDelta)
    set_cursor_pos(max([x,tx]), y, app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

# Return Value: alive?
def resume(fiber):
  try:
    next(fiber)
  except StopIteration:
    return False
  return True

def read_app_text(x, y, x2, y2, digit_only=False):
  rect = getAppRect(True)
  offset = const.getAppOffset()
  x, y = x + offset[0], y + offset[1]
  x2, y2 = x2 + offset[0], y2 + offset[1]
  rect[2], rect[3] = rect[0] + x2, rect[1] + y2
  rect[0], rect[1] = rect[0] + x,  rect[1] + y
  im = ImageGrab.grab(rect)
  filename = 'tmp/apptext.png'
  save_png(im, filename)
  uwait(0.5)
  return img_to_str(filename, digit_only)

def img_to_str(filename, digit_only=False):
  _config = '-psm 12 -psm 13'
  re = pyte.image_to_string(filename, config=_config)
  if digit_only:
    re = correct_digit_result(re)
  return re

def correct_digit_result(re):
  trans = {
    'O': '0',
    'o': '0',
    'D': '0',
    'Z': '2',
    'z': '2',
    '.': '6',
    '/': '8',
    'B': '8',
  }
  return re.translate(str.maketrans(trans))

def get_cursor_pos(app_offset=True):
  mx, my = win32api.GetCursorPos()
  if app_offset:
    offset = const.getAppOffset()
    mx = mx - G.AppRect[0] - offset[0]
    my = my - G.AppRect[1] - offset[1]
  return [mx, my]
