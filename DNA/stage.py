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
  'StageSelect': {
    'pos': ((1025, 388),(611, 739),),
    'color': ((255, 255, 255),(52, 169, 129),)
  },
  'StageMap': {
    'pos': ((159, 1033),(55, 38),(243, 49),),
    'color': ((143, 209, 158),(255, 255, 255),(253, 253, 253),)
  },
  'MissionComplete': {
    'pos': ((1253, 956),(30, 1045),),
    'color': ((225, 180, 84),(255, 255, 255),),
  },
  'RewardSelect': {
    'pos': ((1233, 760),(820, 907),),
    'color': ((0, 0, 0),(219, 175, 82),),
  },
  'FishingReady': {
    'pos': ((1614, 806),(1650, 873),(65, 39),),
    'color': ((253, 253, 253),(253, 253, 253),(253, 253, 253),)
  },
  'FishingMooch': {
    'pos': ((1795, 940),(1812, 974),(64, 40),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),)
  },
  'FishingReward': {
    'pos': ((841, 634),(848, 677),(857, 700),),
    'color': ((209, 209, 209),(209, 209, 209),(19, 17, 12),)
  },
  'FishingReward2': {
    'pos': ((857, 436),(842, 636),(847, 678),),
    'color': ((13, 21, 20),(211, 214, 215),(211, 213, 213),)
  },
  'FishingReward3': {
    'pos': ((867, 436),(842, 635),(846, 676),),
    'color': ((13, 20, 34),(211, 213, 215),(211, 212, 213),)
  },
  'FishingReward4': {
    'pos': ((860, 508),(842, 635),(846, 679),),
    'color': ((14, 26, 34),(211, 213, 215),(211, 213, 213),)
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
    if graphics.is_pixel_match(stg['pos'], stg['color'], True):
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
