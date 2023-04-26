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
    'pos': ((15, 701),(152, 703),(175, 703),(369, 698),(390, 682),),
    'color': ((82, 118, 175),(82, 118, 175),(255, 255, 255),(208, 213, 245),(192, 154, 104),)
  },
  'Profile': {
    'pos': ((19, 708),(125, 700),(226, 694),(329, 699),(259, 686),(142, 625),(45, 616),(168, 580),),
    'color': ((56, 77, 153),(56, 77, 153),(56, 77, 153),(56, 77, 153),(255, 255, 255),(79, 165, 252),(144, 164, 178),(204, 233, 255),)
  },
  'Profile2': {
    'pos': ((17, 700),(87, 705),(123, 698),(232, 701),(257, 688),(389, 701),(46, 617),(379, 642),),
    'color': ((56, 77, 153),(56, 77, 153),(56, 77, 153),(56, 77, 153),(255, 255, 255),(56, 77, 153),(164, 182, 194),(37, 52, 99),)
  },
  'Map': {
    'pos': ((11, 698),(89, 707),(176, 704),(376, 695),(18, 551),),
    'color': ((82, 118, 175),(82, 118, 175),(255, 255, 255),(90, 54, 55),(255, 255, 255),)
  },
  'Map2': {
    'pos': ((6, 696),(86, 705),(172, 704),(377, 696),(381, 541),(345, 726),(404, 680),),
    'color': ((82, 118, 175),(82, 118, 175),(255, 255, 255),(81, 49, 49),(255, 255, 255),(82, 118, 175),(255, 255, 255),)
  },
  'MapSearch': {
    'pos': ((22, 577),(41, 680),(147, 696),(256, 695),(377, 604),(390, 578),(400, 694),(140, 19),),
    'color': ((42, 77, 122),(56, 98, 147),(79, 165, 252),(79, 165, 252),(228, 242, 255),(42, 77, 122),(56, 98, 147),(42, 66, 99),)
  },
  'ConfirmDeploy': {
    'pos': ((117, 258),(77, 308),(78, 379),(69, 456),(242, 459),),
    'color': ((98, 136, 194),(192, 208, 232),(192, 208, 232),(255, 102, 0),(79, 165, 252),)
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
  _G.log_info("Current stage:", s)
  return s and stg in s

def is_map_search_found():
  return graphics.is_pixel_match(position.MapSearchFound[0], position.MapSearchFound[1], True)

def get_dispatched_troop_count():
  cnt = 0
  for pairs in position.MapTroopDispatched:
    if any([graphics.is_pixel_match([pair[0]], [pair[1]], True) for pair in pairs]):
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

def ensure_stage(stg, checks=3, interval=1, handler=None):
  cnt = 0
  while cnt < checks:
    if is_stage(stg):
      cnt += 1
    else:
      cnt = 0
      if handler:
        yield from handler()
    wait(interval)
    yield