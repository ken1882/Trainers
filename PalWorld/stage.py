from copy import copy
from time import sleep
from datetime import datetime
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
  'SelectExpedition': {
    'pos': ((456, 187),(446, 143),),
    'color': ((4, 76, 85),(57, 68, 69),)
  },
  'ExpeditionLoots': {
    'pos': ((787, 190),(1199, 180),(1583, 187),),
    'color': ((102, 124, 128),(57, 68, 69),(102, 124, 128),)
  },
  'ExpeditionPrepare': {
    'pos': ((144, 247),(725, 247),(1086, 493),(1178, 728),),
    'color': ((57, 68, 69),(57, 68, 69),(54, 65, 70),(229, 251, 255),)
  }
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


StageDepth = 0
LastStage = '_'
StageArriveTime = datetime.now()
def reset():
  global StageDepth,LastStage,StageArriveTime
  StageDepth = 0
  LastStage = '_'
  StageArriveTime = datetime.now()
  _G.CurrentStage = None

def is_stage(stg):
  global LastStage,StageDepth,StageArriveTime
  s = get_current_stage()
  if s != LastStage:
    _G.log_info("Current stage:", s)
    LastStage = s
    StageDepth = 0
    StageArriveTime = datetime.now()
  else:
    StageDepth += 1
  return s and stg in s

if __name__ == '__main__':
  while True:
    if Input.is_trigger(win32con.VK_NUMPAD0, True):
      break
    if Input.is_trigger(win32con.VK_NUMPAD1, True):
        print(graphics.get_mouse_pixel())