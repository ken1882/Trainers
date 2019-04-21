import win32api, win32con
import PIL.ImageGrab, time

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
    y += 5
    win32api.SetCursorPos((x, y))
    wait(0.05)
  wait(1)
  mouse_up(x, y)

def scroll_down(x, y, delta = 100):
  mouse_down(x, y)
  ty = y - delta
  wait(0.5)
  while y >= ty:
    y -= 5
    win32api.SetCursorPos((x, y))
    wait(0.01)
  wait(1)
  mouse_up(x, y)

def scroll_left(x, y, delta = 100):
  mouse_down(x, y)
  tx = x + delta
  wait(0.5)
  while x <= tx:
    x += 5
    win32api.SetCursorPos((x, y))
    wait(0.01)
  wait(1)
  mouse_up(x, y)

def scroll_right(x, y, delta = 100):
  mouse_down(x, y)
  tx = x - delta
  wait(0.5)
  while x >= tx:
    x -= 5
    win32api.SetCursorPos((x, y))
    wait(0.01)
  wait(1)
  mouse_up(x, y)