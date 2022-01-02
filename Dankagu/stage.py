from copy import copy
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
  'SongSelect': {
    'pos': ((16, 29),(3, 19),(564, 48),(887, 537),(653, 396),(947, 398),(990, 20),),
    'color': ((116, 99, 85),(241, 240, 224),(97, 84, 77),(255, 181, 2),(67, 49, 36),(97, 84, 77),(107, 91, 79),)
  },
  'PartySelect': {
    'pos': ((31, 17),(61, 16),(69, 539),(73, 566),(414, 541),(918, 540),(990, 325),(749, 198),(339, 170),(343, 198),),
    'color': ((243, 239, 223),(219, 217, 217),(77, 64, 56),(243, 239, 223),(223, 70, 23),(255, 189, 15),(243, 239, 223),(97, 84, 77),(97, 84, 77),(97, 84, 77),)
  },
  'SongClear': {
    'pos': ((516, 104),(517, 146),(536, 309),(561, 298),(795, 310),(979, 455),(524, 411),),
    'color': ((242, 230, 208),(239, 237, 227),(255, 249, 241),(97, 84, 77),(223, 221, 219),(236, 230, 219),(241, 233, 224),)
  },
  'SceneLoading': {
    'pos': ((501, 266),(205, 240),(383, 173),(757, 185),(731, 380),(283, 303),(782, 226),(339, 207),),
    'color': ((0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),)
  },
}

def get_current_stage():
  global Enum
  if _G.LastFrameCount != _G.FrameCount:
    _G.CurrentStage = None
    _G.LastFrameCount = _G.FrameCount
  elif _G.CurrentStage:
    return _G.CurrentStage
  
  for key in Enum:
    stg = Enum[key]
    if graphics.is_pixel_match(stg['pos'], stg['color']):
      _G.CurrentStage = key
      return key
  return None

def check_pixels(pixstruct):
  return graphics.is_pixel_match(pixstruct['pos'], pixstruct['color'])
