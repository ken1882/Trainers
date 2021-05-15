import _G
import os
import win32gui, win32process
from time import sleep
from desktopmagic.screengrab_win32 import (
	getDisplayRects, saveScreenToBmp, saveRectToBmp, getScreenAsImage,
	getRectAsImage, getDisplaysAsImages
)


def remove_ppl():
  os.system(f"{_G.DriverName} /installDriver")
  sleep(0.1)
  os.system(f"{_G.DriverName} /disablePPL {_G.AppPid}")
  sleep(0.1)
  os.system(f"{_G.DriverName} /uninstallDriver")

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

def resize_app_window():
  win32gui.MoveWindow(_G.AppHwnd, _G.AppRect[0], 0, _G.WindowWidth, _G.WindowHeight, True)
  update_app_rect()