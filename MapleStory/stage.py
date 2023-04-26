from copy import copy
from time import sleep
import win32con

import _G
import graphics
import Input
import utils
from _G import log_debug, log_error, log_info, log_warning, resume, uwait, wait
from _G import CVMatchHardRate,CVMatchMinCount,CVMatchStdRate,CVLocalDistance
from utils import img2str, isdigit, ocr_rect
import re

Enum = {
  'Map': {
    'pos': ((868,1034),(878,1014)),
    'color': ((75,73,75),(202,202,202))
  },

}

def get_current_stage():
  global Enum
  for key in Enum:
    stg = Enum[key]
    if graphics.is_pixel_match(stg['pos'], stg['color'], sync=True):
      _G.CurrentStage = key
      return key
  return None

def check_pixels(pixstruct):
  return graphics.is_pixel_match(pixstruct['pos'], pixstruct['color'])

def is_stage(stg):
  s = get_current_stage()
  _G.log_info("Current stage:", s)
  return s and stg in s

if __name__ == '__main__':
  while True:
    if Input.is_trigger(win32con.VK_NUMPAD0, True):
      break
    if Input.is_trigger(win32con.VK_NUMPAD1, True):
        print(graphics.get_mouse_pixel())