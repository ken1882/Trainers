from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait
import Input, position
from random import randint

def start_rabbithole_fiber():
  while True:
    pos = [(752, 384),(869, 341),(489, 293),(899, 501),(878, 517)]
    for i in range(2):
      mx,my = pos[i]
      mx += randint(-10,10)
      my += randint(-10,10)
      Input.moveto(mx,my)
      uwait(0.3)
      Input.click(app_offset=False)
      uwait(0.5)
    for _ in range(24):
      uwait(0.5)
      yield
    for i in range(3):
      mx,my = pos[2+i]
      mx += randint(-10,10)
      my += randint(-10,10)
      Input.moveto(mx,my)
      uwait(0.3)
      Input.click(app_offset=False)
      for _ in range(4):
        uwait(0.5)
        yield
    for _ in range(6):
      uwait(0.5)
      yield
    pos = [(941, 29),(146, 116),(371, 171),(72, 405),(238, 45),(576, 391)]
    for p in pos:
      mx,my = p
      mx += randint(-10,10)
      my += randint(-10,10)
      Input.moveto(mx,my)
      uwait(0.3)
      Input.click(app_offset=False)
      uwait(1.5)
    for _ in range(8):
      uwait(0.5)
      yield
    pos = [(857, 479),(871, 93),(653, 290)]
    for p in pos:
      mx,my = p
      mx += randint(-10,10)
      my += randint(-10,10)
      Input.moveto(mx,my)
      uwait(0.3)
      Input.click(app_offset=False)
      for _ in range(6):
        uwait(0.5)
        yield
    for _ in range(10):
      uwait(0.5)
      yield