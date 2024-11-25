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
  '_': {
    'pos': ((1,1),),
    'color': ((999,999,999),)
  },
  'PowerSaving': {
    'pos': ((1377, 513),(958, 291),(258, 357),(1225, 591),),
    'color': ((153, 227, 252),(81, 98, 134),(19, 21, 27),(162, 213, 246),)
  },
  'Main': {
    'pos': ((503, 596),(325, 81),(71, 268),(597, 80),),
    'color': ((217, 224, 251),(166, 175, 207),(130, 147, 190),(195, 211, 236),)
  },
  'Tavern': {
    'pos': ((338, 263),(103, 726),(1290, 419),),
    'color': ((198, 173, 153),(212, 220, 237),(219, 194, 104),)
  },
  'ChestOpen': {
    'pos': ((1432, 107),(1209, 121),(1224, 146),(803, 147),(544, 162),(1447, 913),),
    'color': ((218, 219, 219),(247, 239, 231),(176, 71, 90),(81, 86, 107),(62, 67, 84),(233, 204, 153),)
  },
  'MusicPlay': {
    'pos': ((1546, 410),(1580, 639),(1573, 820),(1648, 144),(1355, 137),(1669, 882),),
    'color': ((255, 208, 130),(248, 201, 73),(247, 213, 71),(163, 97, 81),(79, 85, 106),(229, 203, 152),)
  },
  'TavernDraw': {
    'pos': ((1448, 163),(1460, 183),(1229, 133),(1273, 437),(1267, 700),(1192, 461),(1258, 816),(1496, 886),),
    'color': ((247, 239, 231),(172, 71, 89),(76, 75, 129),(134, 235, 255),(207, 163, 138),(84, 89, 110),(130, 105, 86),(232, 204, 153),)
  },
  'TavernSign': {
    'pos': ((1604, 133),(1483, 397),(1437, 396),(1387, 396),(1587, 379),(1587, 536),(429, 180),(1586, 884),(1610, 887),),
    'color': ((215, 218, 219),(63, 71, 103),(61, 70, 103),(62, 71, 103),(56, 67, 96),(61, 72, 100),(223, 224, 227),(79, 87, 120),(230, 204, 153),)
  },
  'CharacterProfile_Main': {
    'pos': ((505, 430),(493, 132),(508, 723),(109, 116),(63, 111),(312, 397),),
    'color': ((239, 97, 125),(228, 188, 103),(1, 102, 154),(240, 150, 122),(15, 19, 19),(221, 224, 233),)
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
