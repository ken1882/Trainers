from copy import copy
import enum
from time import sleep

import cv2
import numpy as np
from desktopmagic.screengrab_win32 import getRectAsImage

import _G
import graphics
import Input
import position
import utils
from _G import log_debug, log_error, log_info, log_warning, resume, uwait, wait
from _G import CVMatchHardRate,CVMatchMinCount,CVMatchStdRate,CVLocalDistance
from utils import img2str, isdigit, ocr_rect
import re

Enum = {
  'PowerSaving': {
    'pos': ((1377, 513),(958, 291),(258, 357),(1225, 591),),
    'color': ((153, 227, 252),(81, 98, 134),(19, 21, 27),(162, 213, 246),)
  },
  'Main': {
    'pos': ((503, 596),(325, 81),(71, 268),(597, 80),),
    'color': ((217, 224, 251),(166, 175, 207),(130, 147, 190),(195, 211, 236),)
  },
  'Travern': {
    'pos': ((338, 263),(103, 726),(1290, 419),),
    'color': ((198, 173, 153),(212, 220, 237),(219, 194, 104),)
  }
}

def get_current_stage():
  global Enum
  if graphics.FlagDisableCache or _G.LastFrameCount != _G.FrameCount:
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

LastStage = '_'
def is_stage(stg):
  global LastStage
  s = get_current_stage()
  if s != LastStage:
    _G.log_info("Current stage:", s)
    LastStage = s
  return s and stg in s
