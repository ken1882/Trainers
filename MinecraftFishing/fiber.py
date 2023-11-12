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
