import _G
import win32api, win32con 

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