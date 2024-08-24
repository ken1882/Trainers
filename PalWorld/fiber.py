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
  k = _G.ARGV.key.upper()
  Input.trigger_key(ord(k), True)
  sleep(0.7)
  Input.key_down(ord(k), True)

def start_click_fiber():
  mr = 0
  while True:
    Input.mouse_down(0, 0, use_msg=0,mright=mr)
    sleep(0.03)
    yield
    Input.mouse_up(0, 0, use_msg=0,mright=mr)
