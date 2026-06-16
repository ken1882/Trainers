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
  'GiftConfirm': {
    'pos': ((756, 565), (546, 565)),
    'color': ((255, 203, 0), (252, 252, 254)),
  },
  'StoryPrompt': {
    'pos': ((756, 490), (546, 490)),
    'color': ((255, 203, 0), (252, 252, 254)),
  },
  'AbilityUnlock': {
    'pos': ((756, 543), (546, 543)),
    'color': ((255, 203, 0), (252, 252, 254)),
  },
  'BondLevelUp': {
    'pos': ((650, 170), (790, 415)),
    'color': ((252, 196, 237), (76, 241, 121)),
  },
  'StaffUnlock': {
    'pos': ((610, 685), (660, 685), (680, 685)),
    'color': ((252, 252, 250), (252, 252, 252), (252, 252, 252)),
  },
  'StaffScene': {
    'pos': ((48, 36), (1180, 32)),
    'color': ((194, 195, 198), (40, 13, 47)),
  },
  'CharacterDetail': {
    'pos': ((757, 109),),
    'color': ((33, 137, 207),),
  },
  'GiftPanel': {
    'pos': ((1210, 136), (997, 614)),
    'color': ((252, 252, 252), (205, 38, 118)),
  },
  'ExchangePage': {
    'pos': ((1188, 642), (997, 614)),
    'color': ((252, 252, 252), (28, 22, 28)),
  },
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
LastStageFrame = None
def is_stage(stg, repeat=5):
  global LastStage,StageDepth,LastStageFrame
  s = get_current_stage()
  if _G.FrameCount != LastStageFrame:
    LastStageFrame = _G.FrameCount
    if s == LastStage:
      StageDepth += 1
    else:
      _G.log_info("Current stage:", s)
      LastStage = s
      StageDepth = 1

  return s and stg in s and StageDepth >= repeat
