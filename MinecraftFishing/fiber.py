import _G
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position
from random import randint
import utils
import math
import win32con
from datetime import datetime, timedelta

def start_stripping_fiber():
  cnt = 0
  for i in range(2,10):
    for _ in range(64):
      print(f"Cutting {cnt+1} ({i})")
      Input.key_down(48+i)
      wait(0.1)
      Input.click(0, 0, mright=True)
      wait(0.1)
      Input.key_down(48+1)
      wait(0.1)
      Input.click(0, 0, mright=True)
      wait(0.1)
      cnt += 1
      yield

def start_click_fiber():
  while _G.FlagWorking:
    Input.mouse_down(0,0)
    yield
    Input.mouse_up(0,0)
    yield
  Input.mouse_up(0,0)


def start_press_right_fiber():
  Input.mouse_down(0,0, mright=1)

def start_press_left_fiber():
  Input.mouse_down(0,0)

def start_press_double_fiber():
  rep = _G.ARGV.repeats
  Input.mouse_down(0,0, mright=1)
  wait(0.3)
  Input.mouse_down(0,0)
  for _ in range(rep):
    wait(0.79)
    yield
  Input.mouse_up(0,0, mright=1)
  Input.mouse_up(0,0)

def start_melee_fiber():
  while _G.FlagWorking:
    Input.mouse_down(0,0)
    wait(0.1)
    Input.mouse_up(0,0)
    for _ in range(10):
      wait(0.03)
      yield
  Input.mouse_up(0,0)

def start_xbow_fiber():
  while _G.FlagWorking:
    Input.mouse_down(0,0, mright=1)
    wait(0.1)
    Input.mouse_up(0,0)
    Input.mouse_down(0,0, mright=1)
    for _ in range(15):
      wait(0.1)
      yield
    Input.mouse_up(0,0, mright=1)
    wait(0.1)
  Input.mouse_up(0,0, mright=1)

def start_climb_fiber():
  Input.key_down(win32con.VK_SPACE)

def start_walk_fiber():
  Input.key_down(ord('W'))

def start_fulfill_fiber():
  use_msg = True
  while _G.FlagWorking:
    sy = 340
    sx = 840
    Input.click(sx, sy, use_msg=use_msg)
    yield
    wait(1)
