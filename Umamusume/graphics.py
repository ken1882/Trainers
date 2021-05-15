from win32con import FLASHW_TIMER
from stage import LastFrameCount
import _G
import win32gui
import pytesseract
import input
from desktopmagic.screengrab_win32 import (
	getDisplayRects, saveScreenToBmp, saveRectToBmp, getScreenAsImage,
	getRectAsImage, getDisplaysAsImages
)
from PIL import Image

LastFrameCount = -1
CurrentSnapshot = None
_G.DesktopDC = win32gui.GetDC(0)

def is_color_ok(cur, target):
  for c1,c2 in zip(cur,target):
    if _G.VerboseLevel >= 4:
      print('-'*10)
      print(c1, c2)
    if abs(c1 - c2) > _G.ColorBiasRange:
      return False
  return True

def is_pixel_match(pix, col):
  for i, j in zip(pix, col):
    tx, ty = i
    if not is_color_ok(get_pixel(tx, ty), j):
      return False
  return True

def get_pixel(x,y,sync=False):
  global CurrentSnapshot
  # use win32api to get pixel in real time, slower
  if sync:
    rect = _G.get_full_app_rect()
    x += rect[0]
    y += rect[1]
    rgb = win32gui.GetPixel(_G.DesktopDC, x, y)
    b = (rgb & 0xff0000) >> 16
    g = (rgb & 0x00ff00) >> 8
    r = (rgb & 0x0000ff)
    return (r,g,b)
  # take DC snapshot first, faster
  take_snapshot()
  return CurrentSnapshot.getpixel((x,y))

def get_mouse_pixel(mx=None, my=None):
  if not mx and not my:
    mx, my = input.get_cursor_pos()
  r,g,b = get_pixel(mx, my)
  return ["({}, {}),".format(mx, my), "({}, {}, {}),".format(r,g,b)]

def get_full_rect():
  return (
    _G.AppRect[0] + _G.WinTitleBarSize[0] + _G.WinDesktopBorderOffset[0],
    _G.AppRect[1] + _G.WinTitleBarSize[1] + _G.WinDesktopBorderOffset[1],
    _G.AppRect[2],
    _G.AppRect[3]
  )

def get_content_rect():
  rect = list(win32gui.GetClientRect(_G.AppHwnd))
  rect[0] += _G.WinTitleBarSize[0] + _G.WinDesktopBorderOffset[0]
  rect[1] += _G.WinTitleBarSize[1] + _G.WinDesktopBorderOffset[1]
  rect[2] += _G.WinTitleBarSize[0] + _G.WinDesktopBorderOffset[0]
  rect[3] += _G.WinTitleBarSize[1] + _G.WinDesktopBorderOffset[1]
  return tuple(rect)

def take_snapshot():
  global LastFrameCount,CurrentSnapshot
  if LastFrameCount != _G.FrameCount:
    print("snapshot taken")
    getRectAsImage(get_content_rect()).save(_G.DCSnapshotFile, format='png')
    LastFrameCount = _G.FrameCount
    CurrentSnapshot = Image.open(_G.DCSnapshotFile)
