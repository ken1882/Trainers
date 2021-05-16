import _G, graphics
import win32api, win32con 
import random
from util import wait, uwait

ScrollTime  = 0.03
ScrollDelta = [3,8]

keystate = [0 for _ in range(0xff)]

def update():
  global keystate
  for i in range(0xff):
    if win32api.GetAsyncKeyState(i):
      keystate[i] += 1
    else:
      keystate[i] = 0

def is_trigger(vk):
  return keystate[vk] == 1

def is_pressed(vk):
  return keystate[vk] > 0

def repeat(vk):
  return keystate[vk]

# app_offset: use DC pos instead of global pos
def get_cursor_pos(app_offset=True):
  mx, my = win32api.GetCursorPos()
  if app_offset:
    mx = mx - _G.AppRect[0] - _G.WinTitleBarSize[0] - _G.WinDesktopBorderOffset[0]
    my = my - _G.AppRect[1] - _G.WinTitleBarSize[1] - _G.WinDesktopBorderOffset[1]
  return (mx, my)

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
    rect = graphics.get_content_rect()
    x += rect[0]
    y += rect[1]
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

def mouse_up(x, y, app_offset):
  if app_offset:
    rect = graphics.get_content_rect()
    x += rect[0]
    y += rect[1]
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def set_cursor_pos(x, y, app_offset):
  if app_offset:
    rect = graphics.get_content_rect()
    x += rect[0]
    y += rect[1]
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

def scroll_to(x, y, x2, y2, app_offset=True, haste=False, hold=True):
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