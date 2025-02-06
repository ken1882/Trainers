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
  'Combat': {
    'pos': ((989, 622),(1010, 542),(25, 104),(1009, 632),(53, 628),),
    'color': ((255, 254, 248),(252, 245, 239),(234, 236, 248),(255, 255, 255),(231, 239, 244),)
  },
  'Combat2': {
    'pos': ((988, 621),(1009, 630),(52, 103),(35, 627),),
    'color': ((255, 255, 250),(251, 253, 249),(232, 239, 252),(212, 217, 233),)
  },
  'Combat3': {
    'pos': ((988, 622),(990, 632),(1008, 631),(998, 626),),
    'color': ((255, 255, 255),(255, 255, 253),(254, 255, 251),(78, 78, 78),)
  },
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
