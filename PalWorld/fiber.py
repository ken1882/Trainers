from time import sleep
import win32con,win32api
import _G
from _G import wait, rwait
import Input
import stage, position, graphics
import action

def start_press_fiber():
  Input.key_down(win32con.VK_LBUTTON, True)
  # Input.key_down(ord('F'), True)
  yield

def start_interact_fiber():
  k = _G.ARGV.key.upper()
  while _G.FlagRunning:
    Input.trigger_key(ord(k), True)
    sleep(0.7)
    Input.key_down(ord(k), True)

LastRow = 0
LastCol = 0
def start_click_fiber():
  global LastCol,LastRow
  # for _ in range(20):
  #   Input.click(0,0, use_msg=0)
  #   yield
  for _ in range(_G.ARGV.repeats):
    for pos in ((577, 825),(1403, 726),(1399, 854),):
      Input.click(*pos, use_msg=0)
      sleep(0.1)
      yield
    sleep(0.5)
  return
  # for pos in ((677, 744),(676, 650),(672, 555),(672, 462),(670, 371),):
  #   Input.click(*pos, use_msg=0)
  #   sleep(0.03)
  #   yield
  # return
  for _ in range(_G.ARGV.repeats):
    Input.click(665, 753, use_msg=0,  mright=1)
    sleep(0.03)
    yield
    Input.click(823, 713, use_msg=0)
  return
  dx = 80
  dy = 80
  PalPos = [756, 496]
  SelPalGoods = (256, 380)
  SellSlots = ((383, 372),(379, 457),(391, 567),(397, 657),(393, 728),)
  DoSells = ((526, 384),(737, 265),(835, 931))
  wt = 0.05
  for spos in SellSlots:
    Input.click(*spos, use_msg=0)
    sleep(wt)
    yield
    Input.click(*SelPalGoods, use_msg=0)
    sleep(wt)
    yield
    mx = PalPos[0] + dx*LastCol
    my = PalPos[1] + dy*LastRow
    Input.click(mx, my, use_msg=0)
    LastCol += 1
    if LastCol >= 6:
      LastRow  = (LastRow + 1) % 5
      LastCol  = 0
    sleep(wt)
    yield
    for pos in DoSells:
      Input.click(*pos, use_msg=0)
      sleep(wt)
      yield

def start_production_fiber():
  while True:
    yield
    if Input.is_trigger(win32con.VK_MBUTTON):
      for pos in ((1410, 776),(1247, 867),):
        Input.click(*pos, use_msg=0)
        sleep(0.1)
        yield

def start_buying_fiber():
  while True:
    yield
    if Input.is_trigger(win32con.VK_MBUTTON):
      for pos in ((1392, 703),(1397, 823),):
        Input.click(*pos, use_msg=0)
        sleep(0.1)
        yield

def start_attack_fiber():
  while _G.FlagRunning:
    Input.key_down(1, True)
    for _ in range(9):
      yield
      sleep(0.1)
    Input.key_up(1, True)
    for _ in range(7):
      yield
      sleep(0.1)
    # Input.trigger_key(1, True)
    # for _ in range(5):
    #   yield
    #   sleep(0.1)
    # Input.trigger_key(ord('E'), True)
    # for _ in range(5):
    #   yield
    #   sleep(0.1)
    # Input.trigger_key(ord('C'), True)
    # for _ in range(5):
    #   yield
    #   sleep(0.1)
  Input.key_up(1, True)
