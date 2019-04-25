import win32api, win32con
import PIL.ImageGrab, time, random

ScrollTime  = 0.03
ScrollDelta = [3,8]
def getPixel(x=None, y=None):
  if x and y:
    return PIL.ImageGrab.grab().load()[x, y]
  return PIL.ImageGrab.grab().load()

def mouse_down(x,y):
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

def mouse_up(x,y):
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def click(x, y):
  win32api.SetCursorPos((x,y))
  mouse_down(x,y)
  mouse_up(x,y)

def wait(sec):
  time.sleep(sec)

def scroll_up(x, y, delta = 100):
  mouse_down(x, y)
  ty = y + delta
  wait(0.5)
  while y <= ty:
    y += random.randint(*ScrollDelta)
    win32api.SetCursorPos((x, y))
    wait(ScrollTime)
  mouse_up(x, y)

def scroll_down(x, y, delta = 100):
  mouse_down(x, y)
  ty = y - delta
  wait(0.5)
  while y >= ty:
    y -= random.randint(*ScrollDelta)
    win32api.SetCursorPos((x, y))
    wait(ScrollTime)
  mouse_up(x, y)

def scroll_left(x, y, delta = 100):
  mouse_down(x, y)
  tx = x + delta
  wait(0.5)
  while x <= tx:
    x += random.randint(*ScrollDelta)
    win32api.SetCursorPos((x, y))
    wait(ScrollTime)
  mouse_up(x, y)

def scroll_right(x, y, delta = 100):
  mouse_down(x, y)
  tx = x - delta
  wait(0.5)
  while x >= tx:
    x -= random.randint(*ScrollDelta)
    win32api.SetCursorPos((x, y))
    wait(ScrollTime)
  mouse_up(x, y)