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
  'Finished': {
    'pos': ((485, 241),(1168, 173),(360, 406),(1483, 794),),
    'color': ((242, 223, 192),(250, 234, 206),(214, 158, 90),(255, 131, 156),)
  },
  'QuestSelect': {
    'pos': ((94, 36),(1381, 29),(700, 829),(547, 813),),
    'color': ((252, 241, 233),(80, 70, 70),(224, 155, 85),(134, 91, 82),)
  },
  'QuestInfo': {
    'pos': ((1140, 182),(1321, 708),(696, 593),(1403, 563),(97, 132),(212, 748),),
    'color': ((79, 70, 71),(252, 97, 123),(181, 255, 239),(71, 70, 71),(95, 148, 84),(107, 203, 89),)
  },
  'Battle': {
    'pos': ((1503, 44),(53, 665),(386, 32),(1414, 49),(386, 58),),
    'color': ((219, 209, 202),(193, 177, 164),(134, 252, 181),(222, 213, 204),(49, 51, 49),)
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
