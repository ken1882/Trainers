from time import sleep
import win32con,win32api
import _G
from _G import uwait
import Input
import stage, position, graphics

def start_press_fiber():
  Input.key_down(win32con.VK_SPACE, True)
  yield

def start_gathering_fiber():
  while True:
    Input.trigger_key(ord('E'), True)
    yield