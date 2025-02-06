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
  'ManaRefill': {
    'pos': ((311, 60),(1194, 667),(1220, 667),(326, 63),(172, 29),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(38, 64, 98),)
  },
  'ManaRefill2': {
    'pos': ((135, 472),(1206, 389),(1213, 668),(1178, 73),(105, 69),),
    'color': ((84, 84, 186),(70, 84, 132),(255, 255, 255),(70, 80, 122),(52, 72, 118),)
  },
  'ManaRefill3': {
    'pos': ((98, 143),(1217, 668),(1071, 263),(1095, 340),),
    'color': ((66, 88, 146),(255, 255, 255),(62, 84, 144),(62, 84, 144),)
  },
  'AttackPhase': {
    'pos': ((599, 604),(1203, 667),(1105, 664),(41, 315),),
    'color': ((118, 123, 123),(255, 255, 255),(255, 255, 255),(60, 76, 91),)
  },
  'AttackPhase2': {
    'pos': ((1208, 669),(1136, 658),(853, 691),(145, 661),),
    'color': ((255, 255, 255),(32, 31, 33),(96, 94, 97),(255, 255, 255),)
  },
  'StandbyPhase': {
    'pos': ((195, 576),(1248, 336),(1203, 667),(160, 203),),
    'color': ((124, 142, 165),(54, 72, 90),(255, 255, 255),(66, 76, 114),)
  },
  'StandbyPhase2': {
    'pos': ((188, 570),(1176, 239),(1219, 668),),
    'color': ((110, 136, 156),(52, 76, 92),(255, 255, 255),)
  },
  'Combat': {
    'pos': ((1192, 661),(1220, 667),(43, 28),(528, 625),(1220, 558),),
    'color': ((255, 255, 255),(255, 255, 255),(221, 222, 234),(248, 248, 248),(255, 255, 255),)
  },
  'Combat2': {
    'pos': ((1213, 666),(1193, 658),(1105, 663),(58, 665),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),)
  },
  'Combat3': {
    'pos': ((247, 656),(1107, 657),(1196, 665),(1218, 666),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),)
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

'''
------------------------------------------
((1215, 532),(1126, 442),(933, 411),(1194, 668),)
------------------------------------------
((244, 244, 244),(241, 171, 184),(247, 175, 189),(255, 255, 255),)


-----------------------------------------
((1228, 147),(1251, 259),(1195, 667),(536, 533),(193, 574),)
------------------------------------------
Received termination signal
((35, 50, 64),(52, 74, 90),(255, 255, 255),(10, 203, 240),(112, 134, 157),)
'''