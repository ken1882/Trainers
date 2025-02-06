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
  'NormalCombatVictory': {
    'pos': ((49, 619),(112, 620),(50, 60),(858, 630),(748, 653),),
    'color': ((18, 155, 254),(19, 155, 254),(254, 254, 254),(136, 135, 134),(30, 6, 1),)
  },
  'NormalCombatVictory2': {
    'pos': ((68, 607),(835, 608),(50, 60),),
    'color': ((34, 157, 254),(179, 179, 178),(254, 254, 254),)
  },
  'NormalCombatVictory3': {
    'pos': ((42, 625),(762, 648),(50, 59),(724, 435),(632, 674),),
    'color': ((254, 222, 23),(219, 218, 217),(254, 254, 254),(183, 65, 33),(254, 254, 57),)
  },
  'NormalCombatVictory4': {
    'pos': ((45, 624),(49, 56),(721, 436),(835, 609),),
    'color': ((254, 224, 16),(254, 254, 254),(183, 65, 34),(180, 179, 178),)
  },
  'NormalCombatVictory5': {
    'pos': (((43, 622),(935, 688),(50, 59),)),
    'color': (((65, 162, 254),(5, 1, 0),(254, 254, 254),))
  },
  'RaidCombatVictory': {
    'pos': ((32, 308),(31, 354),(835, 618),(50, 59),(1040, 611),),
    'color': ((254, 83, 7),(254, 83, 7),(180, 179, 178),(254, 254, 254),(179, 179, 178),)
  },
  'RaidCombatVictory2': {
    'pos': ((51, 59),(29, 306),(29, 398),(808, 405),(800, 474),),
    'color': ((254, 254, 254),(254, 104, 44),(254, 101, 40),(254, 244, 164),(254, 191, 185),)
  },
  'RaidCombatVictory3': {
    'pos': ((48, 60),(29, 308),(28, 399),(808, 405),(800, 474),),
    'color': ((254, 254, 254),(254, 91, 31),(254, 94, 37),(254, 244, 164),(254, 191, 185),)
  },
  'RaidCombatVictory4': {
    'pos': ((51, 62),(29, 306),(30, 399),(811, 400),(801, 474),),
    'color': ((254, 254, 254),(254, 89, 28),(254, 86, 21),(254, 244, 168),(254, 190, 185),)
  },
  'MinigameDropEnd': {
    'pos': ((124, 165),(332, 610),(951, 618),(213, 168),),
    'color': ((254, 251, 239),(35, 213, 186),(32, 221, 188),(254, 254, 254),)
  },
  'FishingMind': {
    'pos': ((133, 58),(281, 58),(519, 73),(751, 71),(967, 76),),
    'color': ((0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),)
  },
  'CafeMain': {
    'pos': ((21, 24),(348, 40),(117, 542),(94, 688),(1207, 542),(1179, 694),),
    'color': ((205, 45, 65),(221, 215, 220),(254, 254, 253),(230, 236, 248),(111, 141, 252),(230, 236, 246),)
  },
  'GeneralOK': {
    'pos': ((607, 641),(646, 633),(665, 650),),
    'color': ((253, 253, 253),(254, 254, 254),(253, 253, 253),)
  },
  'GeneralOK2': {
    'pos': ((1214, 47),(1245, 48),(599, 660),(684, 649),(684, 672),(664, 659),),
    'color': ((162, 180, 253),(163, 180, 253),(254, 254, 254),(254, 254, 254),(254, 254, 254),(254, 254, 254),)
  },
  'ObtainRelic': {
    'pos': ((630, 512),(653, 148),(947, 239),(897, 620),(141, 92),),
    'color': ((164, 133, 117),(141, 111, 99),(27, 10, 2),(161, 130, 114),(254, 254, 237),)
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
