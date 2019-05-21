import win32api, win32gui, win32ui, win32con, const
import PIL.ImageGrab, time, random, math, G
import numpy as np
from G import uwait, wait
from PIL import Image
from PIL import ImageGrab
from ctypes import windll
from datetime import datetime
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

def print_window(saveimg=False):
  im = ImageGrab.grab(getAppRect(True))
  try:
    if G.is_mode_slime() or saveimg:
      im.save(G.ScreenImageFile)
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
    return ScreenSnapShot[1][x, y]
  return ScreenSnapShot[1]

def flush_screen_cache():
  ScreenSnapShot[0] = 0

def find_app():
  # Callback function for EnumWindows
  def callback(handle, data):
    if win32gui.GetWindowText(handle) != G.AppName:
      return 
    try:
      rect = win32gui.GetWindowRect(handle)
      x, y, w, h = rect
      w, h = w-x,h-y
      win32gui.MoveWindow(handle, x, y, w, h, 1)
      G.AppHwnd = handle
    except Exception:
      pass
  win32gui.EnumWindows(callback, None)
  if G.AppHwnd == 0:
    print("Unable to find app window, aborting")
    exit()
  else:
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
  win32gui.MoveWindow(G.AppHwnd, wx, wy, G.AppWidth, G.AppHeight, 1)
  uwait(1)
  getAppRect()

# Reset window position for restarting
def reset_window():
  rect = getAppRect()
  _, _, w, h = rect
  win32gui.MoveWindow(G.AppHwnd, 0, 0, w, h, 1)

def mouse_down(x,y):
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

def mouse_up(x,y):
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def click(x, y, app_offset=True):
  if app_offset:
    x += G.AppRect[0]
    y += G.AppRect[1]
  win32api.SetCursorPos((x,y))
  mouse_down(x,y)
  mouse_up(x,y)

def scroll_up(x, y, delta = 100, app_offset=True, haste=False):
  if app_offset:
    x += G.AppRect[0]
    y += G.AppRect[1]
  mouse_down(x, y)
  ty = y + delta
  wait(0.01 if haste else 0.5)
  while y <= ty:
    y += random.randint(*ScrollDelta)
    win32api.SetCursorPos((x, min([y,ty])))
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y)

def scroll_down(x, y, delta = 100, app_offset=True, haste=False):
  if app_offset:
    x += G.AppRect[0]
    y += G.AppRect[1]
  mouse_down(x, y)
  ty = y - delta
  wait(0.01 if haste else 0.5)
  while y >= ty:
    y -= random.randint(*ScrollDelta)
    win32api.SetCursorPos((x, max([y,ty])))
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y)

def scroll_left(x, y, delta = 100, app_offset=True, haste=False):
  if app_offset:
    x += G.AppRect[0]
    y += G.AppRect[1]
  mouse_down(x, y)
  tx = x + delta
  wait(0.01 if haste else 0.5)
  while x <= tx:
    x += random.randint(*ScrollDelta)
    win32api.SetCursorPos((min([x,tx]), y))
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y)

def scroll_right(x, y, delta = 100, app_offset=True, haste=False):
  if app_offset:
    x += G.AppRect[0]
    y += G.AppRect[1]
  mouse_down(x, y)
  tx = x - delta
  wait(0.01 if haste else 0.5)
  while x >= tx:
    x -= random.randint(*ScrollDelta)
    win32api.SetCursorPos((max([x,tx]), y))
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y)

# Return Value: alive?
def resume(fiber):
  try:
    next(fiber)
  except StopIteration:
    return False
  return True

def read_app_text(x, y, x2, y2, digit_only=False):
  rect = getAppRect(True)
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
    'D': '0',
    'Z': '2',
    'z': '2',
    '/': '8',
  }
  return re.translate(str.maketrans(trans))

def get_app_cursor_pos():
  mx, my = win32api.GetCursorPos()
  mx, my = mx - G.AppRect[0], my - G.AppRect[1]
  return [mx, my]
