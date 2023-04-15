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
  'Home': {
    'pos': ((8, 713),(117, 721),(151, 716),(167, 715),(361, 710),),
    'color': ((82, 118, 175),(82, 118, 175),(82, 118, 175),(255, 255, 255),(216, 223, 255),)
  },
  'QuitGame': {
    'pos': ((98, 270),(282, 269),(108, 357),(304, 376),(64, 466),(233, 469),),
    'color': ((98, 136, 194),(98, 136, 194),(192, 208, 232),(192, 208, 232),(255, 102, 0),(79, 165, 252),)
  },
  'Profile': {
    'pos': ((18, 34),(16, 709),(54, 712),(121, 709),(251, 700),(376, 709),(133, 636),(39, 629),(357, 662),),
    'color': ((203, 255, 255),(56, 77, 153),(255, 255, 255),(56, 77, 153),(255, 255, 255),(56, 77, 153),(79, 165, 252),(160, 181, 196),(37, 52, 99),)
  },
  'Map': {
    'pos': ((9, 707),(126, 717),(167, 718),(341, 734),(369, 707),(366, 691),(12, 561),),
    'color': ((82, 118, 175),(82, 118, 175),(255, 255, 255),(82, 118, 175),(90, 54, 55),(255, 254, 205),(255, 255, 255),)
  },
  'Map2': {
    'pos': ((370, 708),(282, 713),(207, 716),(165, 717),(4, 713),(9, 133),),
    'color': ((90, 54, 55),(82, 118, 175),(82, 118, 175),(255, 255, 255),(82, 118, 175),(241, 249, 253),)
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

def is_stage(stg):
  s = get_current_stage()
  return s and stg in s

def is_map_search_found():
  return graphics.is_pixel_match(position.MapSearchFound[0], position.MapSearchFound[1], True)

def get_dispatched_troop_count():
  cnt = 0
  for pair in position.MapTroopDispatched:
    if graphics.is_pixel_match([pair[0]], [pair[1]], True):
      cnt += 1
  return cnt

def get_assigned_hero_index():
  ret = []
  idx = 1
  for pix,col in zip(*position.TroopHeroAssigned):
    if graphics.is_pixel_match([pix], [col], True):
      ret.append(idx)
    idx += 1
  return ret