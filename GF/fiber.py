from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait
import Input, position, graphics
from random import randint

def start_rabbithole_fiber():
  while True:
    pos = [
      (811, 383),(869, 341), # stage select
      (488, 296),(899, 501),(878, 517) # deploy
    ]
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
    # battle start
    pos = [
      (941, 29),(146, 116), # skip
      (263, 95),(72, 405),(238, 45),(576, 391) # build teleporter
    ]
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

def start_visit_fiber():
  LikePos = ((865, 539),(874, 514),(961, 523),)
  LikeCol = ((50, 50, 50),(221, 221, 221),(221, 221, 221),)
  while True:
    if not graphics.is_pixel_match(LikePos, LikeCol):
      break
    mx,my = (908, 523)
    Input.moveto(mx+randint(-10,10), my+randint(-10,10))
    uwait(0.3)
    Input.click()
    uwait(0.5)
    mx,my = (184, 523)
    Input.moveto(mx+randint(-10,10), my+randint(-10,10))
    uwait(0.3)
    Input.click()
    for _ in range(6):
      uwait(0.5)
      yield