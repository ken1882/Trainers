import os, win32api, win32gui, win32ui, win32con, win32process, win32com.client
import const, re
import cv2, time, random, math, G, Input
import numpy as np
from G import uwait, wait
from PIL import Image
from PIL import ImageGrab
from ctypes import windll
from datetime import timedelta
from datetime import datetime
from os import system
import pytesseract as pyte

ScrollTime  = 0.03
ScrollDelta = [3,8]
Initialized = False
LastAppRect = np.array([0,0,0,0])
LastFrameCount = -1
Shell = None

def initialize():
  global Shell, Initialized
  Initialized = True
  Shell = win32com.client.Dispatch("WScript.Shell")
  const.ScreenResoultion[0] = win32api.GetSystemMetrics(0)
  const.ScreenResoultion[1] = win32api.GetSystemMetrics(1)

def bulk_get_kwargs(*args, **kwargs):
  result = []
  for info in args:
    name, default = info
    arg = kwargs.get(name)
    arg = default if arg is None else arg
    result.append(arg)
  return result

def change_title(nt):
  system("title " + nt)

def getWindowPixels(rect, saveimg=False, filename=None):
  im = ImageGrab.grab(rect)
  try:
    if saveimg and filename:
      im.save(filename)
  except Exception as err:
    print("Failed to save image:", err)
  pixels = im.load()
  return pixels

LastOutputFrame = -1
def print_window(saveimg=False, filename=G.ScreenImageFile):
  global LastOutputFrame
  if LastOutputFrame == G.FrameCount:
    saveimg = False
  return getWindowPixels(getAppRect(True), saveimg, filename)

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

def get_current_time_sec():
  return int(time.time())

ScreenSnapShot = [hash_timenow(), ImageGrab.grab().load()]

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
  global ScreenSnapShot, LastFrameCount, LastOutputFrame
  ScreenSnapShot[0] = 2147483647
  LastFrameCount = -1
  LastOutputFrame = -1

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
      regex = const.TargetAppRegex[name]
      if not re.search(regex, title):
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
  target_app = max(target_cnt, key=(lambda k:target_cnt[k]))
  if G.FlagDebug:
    print("Target App count:", target_cnt)
    print(target_app, possibles)
  possibles.sort(key=lambda ss: len(ss[0])-len(target_app)+ss[0].index(target_app))
  if possibles:
    pid = choose_best_hwnd(possibles, target_app)
    if G.FlagDebug:
      print("Final:", print(pid, possibles[pid][1]))
    if pid >= 0:
      const.AppName = target_app
      G.AppHwnd = possibles[pid][1]
  
  if G.AppHwnd == 0:
    print("Unable to find app window")
  else:
    print("Current App:", const.AppName)
    getAppRect()
  

# ori: return original 4 pos of the window
def getAppRect(ori=False):
  global LastAppRect
  if G.AppHwnd == 0:
    print("App not ready")
    return [0, 0, const.ScreenResoultion[0], const.ScreenResoultion[1]]
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

def random_pos(x, y, rrange=G.DefaultRandRange):
  x += random.randint(-rrange, rrange)
  y += random.randint(-rrange, rrange)
  return [x, y]

def key_down(*args):
  for kid in args:
    win32api.keybd_event(kid, 0, 0, 0)

def key_up(*args):
  for kid in args:
    win32api.keybd_event(kid, 0, win32con.KEYEVENTF_KEYUP, 0)

def trigger_key(*args):
  for kid in args:
    key_down(kid)
  uwait(0.03)
  for kid in args:
    key_up(kid)

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
    y += (random.randint(*ScrollDelta) + haste * 2)
    set_cursor_pos(x, min([y,ty]), app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_down(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  ty = y - delta
  wait(0.01 if haste else 0.5)
  while y >= ty:
    y -= (random.randint(*ScrollDelta) + haste * 2)
    set_cursor_pos(x, max([y,ty]), app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_left(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  tx = x + delta
  wait(0.01 if haste else 0.5)
  while x <= tx:
    x += (random.randint(*ScrollDelta) + haste * 2)
    set_cursor_pos(min([x,tx]), y, app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_right(x, y, delta = 100, app_offset=True, haste=False):
  mouse_down(x, y, app_offset)
  tx = x - delta
  wait(0.01 if haste else 0.5)
  while x >= tx:
    x -= (random.randint(*ScrollDelta) + haste * 2)
    set_cursor_pos(max([x,tx]), y, app_offset)
    wait(0.01 if haste else ScrollTime)
  mouse_up(x, y, app_offset)

def scroll_to(x, y, x2, y2, **kwargs):
  app_offset,haste,hold = bulk_get_kwargs(
    ('app_offset', True), ('haste', False), ('hold', True),
    **kwargs
    )
  
  mouse_down(x, y, app_offset)
  wait(0.01 if haste else ScrollTime)
  tdx, tdy = abs(x2 - x), abs(y2 - y)
  try:
    pcx, pcy = tdx // tdy, tdy // tdx
    pcx, pcy = min([max([pcx, 0.4]), 2]), min([max([pcy, 0.4]), 2])
  except Exception:
    pcx, pcy = 1, 1

  while x != x2 or y != y2:
    dx = int((random.randint(*ScrollDelta) + haste * 2) * pcx)
    dy = int((random.randint(*ScrollDelta) + haste * 2) * pcy)
    x = min([x2, x+dx]) if x2 > x else max([x2, x-dx])
    y = min([y2, y+dy]) if y2 > y else max([y2, y-dy])
    set_cursor_pos(x, y, app_offset)
    wait(0.01 if haste else ScrollTime)
  if hold:
    uwait(1)
  mouse_up(x, y, app_offset)

# Return Value: alive?
def resume(fiber):
  try:
    next(fiber)
  except StopIteration:
    return False
  return True

def read_app_text(x, y, x2, y2, **kwargs):
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
  return img_to_str(filename, **kwargs)

def img_to_str(filename, **kwargs):
  dtype, lan = bulk_get_kwargs(
    ('dtype', None), ('lan', 'eng'),
    **kwargs
  )
  print("----------\nOCR Processing")
  _config = '-psm 12 -psm 13'
  rescues = 2
  result = None
  for _ in range(rescues+1):
    try:
      result = pyte.image_to_string(filename, config=_config, lang=lan)
      break
    except Exception as err:
      if "unknown command line argument '-psm'" in str(err):
        _config = _config.replace('-psm', '--psm')
      if "TESSDATA_PREFIX" in str(err):
        os.environ['TESSDATA_PREFIX'] += '\\tessdata'
      
  if dtype == 'digit':
    result = correct_digit_result(result)
  elif dtype == 'time':
    result = correct_time_result(result)
    
  print("OCR Result:\n{}\n".format(result))
  return result

def sec2readable(secs):
  return str(timedelta(seconds=secs))

def correct_digit_result(result):
  print("Before digit tr:", result)
  result = result.translate(str.maketrans(const.OCRDigitTrans))
  return ''.join(ch for ch in result if ch.isdigit())

def correct_time_result(result):
  print("Before time tr:", result)
  result = result.translate(str.maketrans(const.OCRDigitTrans))
  return ''.join(ch for ch in result if ch.isdigit() or ch == ':')

def get_cursor_pos(app_offset=True):
  mx, my = win32api.GetCursorPos()
  if app_offset:
    offset = const.getAppOffset()
    mx = mx - G.AppRect[0] - offset[0]
    my = my - G.AppRect[1] - offset[1]
  return [mx, my]

def zoomout(rep=1):
  for _ in range(rep):
    trigger_key(Input.keymap.kMINUS)
    uwait(0.05)

def zoomin(rep=1):
  for _ in range(rep):
    trigger_key(Input.keymap.kEQUAL)
    uwait(0.05)

def get_image_locations(img, threshold=.89):
  print_window(True)
  img_rgb  = cv2.imread(G.ScreenImageFile)
  template = cv2.imread(img)
  res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
  loc = np.where(res >= threshold)
  h, w = template.shape[:-1]
  result = []
  for pt in zip(*loc[::-1]):  # Switch collumns and rows
    result.append(pt)
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
  if G.FlagDebug:
    cv2.imwrite('tmp/result.png', img_rgb)
  return result

def find_tweaker():
  wx, wy, ww, wh = 0, 0, const.BSTResoultion[0], const.BSTResoultion[1]
  def callback(handle, data):
    nonlocal wx, wy
    title = win32gui.GetWindowText(handle)
    if const.BSTTitle not in title:
      return
    try:
      rect = win32gui.GetWindowRect(handle)
      x, y, w, h = rect
      w, h = w-x,h-y
      win32gui.MoveWindow(handle, x, y, w, h, 1)
      wx, wy = x, y
      G.BSTHwnd = int(handle)
      G.BSTRect = [wx, wy, ww, wh]
    except Exception:
      pass
  win32gui.EnumWindows(callback, None)
  if G.BSTHwnd > 0:
    win32gui.MoveWindow(G.BSTHwnd, wx, wy, ww, wh, 1)
    print("BST found:", hex(G.BSTHwnd))
    # returns original winrect
    return [wx, wy, wx+ww, wy+wh]

def activeWindow(hwnd):
  global Shell
  Shell.SendKeys('%')
  pid = win32process.GetWindowThreadProcessId(hwnd)[1]
  windll.user32.AllowSetForegroundWindow(pid)
  win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
  win32gui.BringWindowToTop(hwnd)
  win32gui.SetActiveWindow(hwnd)
  windll.user32.SwitchToThisWindow(hwnd, 1)
  win32gui.SetForegroundWindow(hwnd)

def wait_cont(sec):
  times = int(sec // 0.5)
  for _ in range(times):
    sec = max([0.01, 0.5 - G.FPS * G.InternUpdateTime])
    uwait(sec)
    yield