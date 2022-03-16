import win32con
import _G
from _G import uwait
import Input
import Arcana_UpperPath,StarryOcean4
from utils import spawn_childproc

def start_click_fiber():
  cnt = int(_G.ConsoleArgv.ntimes)
  for _ in range(cnt):
    Input.click()
    uwait(0.1)
    Input.click()
    uwait(0.03)
    yield

def start_starry_ocean():
  name = 'macro_main'
  spawn_childproc(name, StarryOcean4.start_main)
  _G.MainChild = _G.ChildProcess[name]
  _G.MainChildPipe = _G.ChildPipe[name]
  _G.MainChildName = name
  print("Chlid proc started")

def start_test_fiber():
  pass