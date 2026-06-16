from copy import copy
import enum
from time import sleep

import cv2
import numpy as np
from desktopmagic.screengrab_win32 import getRectAsImage

import _G
import graphics
import position
import utils
from _G import log_debug, log_error, log_info, log_warning, resume, uwait, wait
from _G import CVMatchHardRate,CVMatchMinCount,CVMatchStdRate,CVLocalDistance
from utils import img2str, isdigit, ocr_rect
import re

Enum = {
  'MainMenu': {
    'pos': ((551, 201),(597, 265),(539, 349),(1333, 354),),
    'color': ((59, 67, 48),(51, 57, 42),(131, 25, 6),(131, 25, 6),)
  },
  'GenComplete': {
    'pos': ((33, 377),(130, 378),(29, 348),(124, 351),(525, 370),),
    'color': ((24, 124, 54),(24, 124, 54),(24, 124, 54),(24, 124, 54),(75, 75, 75),)
  },
  'GenComplete2': {
    'pos': ((30, 353),(33, 382),(160, 352),(535, 379),),
    'color': ((24, 124, 54),(24, 124, 54),(75, 75, 75),(75, 75, 75),),
  }
}

def get_current_stage():
  global Enum
  if _G.LastFrameCount != _G.FrameCount:
    _G.CurrentStage = None
    _G.LastFrameCount = _G.FrameCount
  else:
    return _G.CurrentStage
  
  for key in Enum:
    stg = Enum[key]
    if graphics.is_pixel_match(stg['pos'], stg['color']):
      _G.CurrentStage = key
      return key

  return None

def check_pixels(pixstruct):
  return graphics.is_pixel_match(pixstruct['pos'], pixstruct['color'])

StageDepth = 0
LastStage = '_'
def is_stage(stg):
  global LastStage,StageDepth
  s = get_current_stage()
  if s != LastStage:
    _G.log_info("Current stage:", s)
    LastStage = s
    StageDepth = 0
  else:
    StageDepth += 1
  return s and stg in s
