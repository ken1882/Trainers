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
  'MirrorRanking': {
    'pos': ((0, 442),(1, 470),(386, 354),(404, 320),(405, 394),(757, 107),),
    'color': ((30, 44, 66),(104, 69, 171),(255, 255, 255),(65, 37, 122),(104, 69, 171),(30, 44, 66),),
  },
  'CombatPlayerTurn': {
    'pos': ((911, 28),(960, 39),(899, 465),(910, 504),(894, 512),(877, 512),(945, 499),(960, 488),),
    'color': ((255, 255, 255),(246, 239, 226),(245, 239, 216),(249, 245, 234),(242, 212, 114),(212, 187, 66),(249, 245, 235),(237, 200, 78),)
  },
  'CombatPlayerTurn2': {
    'pos': ((919, 27),(968, 37),(889, 509),(916, 509),(930, 491),(951, 501),(870, 502),(907, 469),),
    'color': ((255, 255, 255),(248, 242, 231),(218, 193, 78),(249, 246, 235),(154, 121, 84),(249, 245, 234),(249, 245, 234),(246, 243, 229),)
  },
  'RankingBattleEnd': {
    'pos': ((303, 249),(308, 308),(611, 256),(613, 303),(234, 362),(241, 393),(4, 554),(125, 557),),
    'color': ((104, 69, 171),(104, 69, 171),(255, 255, 255),(255, 255, 255),(104, 69, 171),(31, 45, 67),(30, 44, 66),(255, 255, 255),)
  },
  'MirrorLevel': {
    'pos': ((1, 85),(3, 109),(12, 434),(11, 472),(786, 107),(404, 318),(406, 300),),
    'color': ((0, 94, 194),(255, 255, 255),(30, 44, 66),(0, 94, 194),(30, 44, 66),(0, 66, 138),(0, 94, 194),)
  },
  'MirrorLevelBattleEnd': {
    'pos': ((222, 330),(232, 381),(592, 345),(587, 389),(236, 425),(231, 460),(1, 551),(125, 554),),
    'color': ((0, 94, 194),(0, 95, 194),(255, 255, 255),(255, 255, 255),(0, 94, 193),(30, 44, 67),(30, 44, 66),(255, 255, 255),)
  },
  'MirrorPvPSelection': {
    'pos': ((1, 146),(942, 137),(362, 553),(239, 314),(579, 312),),
    'color': ((32, 45, 66),(50, 34, 94),(25, 38, 56),(0, 92, 188),(97, 66, 163),)
  },
  'MirrorVicotry': {
    'pos': ((361, 195),(613, 195),(491, 289),),
    'color': ((203, 185, 116),(203, 185, 116),(221, 205, 120),)
  },
  'MirrorDefeat': {
    'pos': ((382, 281),(451, 290),(542, 298),(585, 296),),
    'color': ((213, 211, 209),(178, 170, 169),(160, 144, 132),(169, 157, 145),)
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
