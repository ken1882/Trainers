from time import sleep
import win32con,win32api
import _G
from _G import uwait
import Input
import stage, position, graphics

def start_press_fiber():
  Input.key_down(win32con.VK_SPACE, True)
  yield

def start_interact_fiber():
  Input.trigger_key(ord('F'), True)
  sleep(0.7)
  Input.key_down(ord('F'), True)

def start_click_fiber():
  while True:
    Input.mouse_down(0, 0, use_msg=1,mright=1)
    yield
    Input.mouse_up(0, 0, use_msg=1,mright=1)
