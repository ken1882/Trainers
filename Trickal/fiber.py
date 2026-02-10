import _G
from _G import rwait, wait, uwait, log_info
import Input, position, graphics, stage
from random import randint
import action, utils
import math
import win32con
from datetime import datetime, timedelta

def _is_ediable():
  uneditable_icon = (
    ((422, 240),(412, 238),),
    ((247, 215, 217),(247, 161, 167),),
  )
  return not graphics.is_pixel_match(*uneditable_icon)

def start_restaurant_fiber():
  while True:
    yield
    while not stage.is_stage('RestaurantMain'):
      yield from rwait(1.0)
    Input.rclick(625,170)
    yield from rwait(1.0)
    if not _is_ediable():
      break
    Input.rclick(366, 242)
    while not stage.is_stage('RestaurantMain'):
      yield
    Input.rclick(617, 556)
    uwait(0.5)
    # Input.rclick(195, 300)
    # uwait(0.3)
    Input.rclick(945, 695)
    yield
    while not stage.is_stage('RestaurantMain'):
      Input.rclick(400, 366)
      Input.rclick(400, 366)
      Input.rclick(400, 366)
      uwait(0.5)
      Input.rclick(932, 594)
      yield