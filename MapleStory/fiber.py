import win32con
import _G
from _G import uwait
import Input
import Arcana_UpperPath

def start_click_fiber():
  cnt = int(_G.ConsoleArgv.ntimes)
  for _ in range(cnt):
    Input.click()
    uwait(0.1)
    Input.click()
    uwait(0.03)
    yield

def get_keybd_pair(code):
  yield Input.Keyboard(code)
  yield Input.Keyboard(code, win32con.KEYEVENTF_KEYUP)

def start_test_fiber():
  pass