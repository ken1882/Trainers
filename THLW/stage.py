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
    'pos': ((129, 472),(175, 523),(36, 33),(485, 31),(649, 32),(446, 59),),
    'color': ((255, 255, 237),(255, 255, 237),(118, 138, 166),(117, 176, 212),(118, 32, 18),(215, 163, 85),)
  },
  'HelperSelect': {
    'pos': ((36, 40),(55, 102),(95, 112),(287, 111),(332, 218),(731, 217),(485, 30),(909, 508),),
    'color': ((108, 120, 138),(211, 161, 71),(211, 161, 71),(211, 161, 71),(235, 235, 235),(235, 235, 231),(118, 178, 214),(121, 121, 121),),
  },
  'CombatPrepare': {
    'pos': ((35, 33),(51, 480),(68, 359),(241, 389),(410, 423),(752, 505),(679, 192),(680, 234),(677, 308),),
    'color': ((118, 139, 168),(241, 235, 223),(200, 68, 43),(48, 112, 182),(251, 177, 40),(232, 57, 16),(65, 102, 121),(65, 100, 121),(65, 102, 121),)
  },
  'SceneStory': {
    'pos': ((902, 37),(901, 48),(914, 51),(950, 48),(953, 39),(923, 45),(936, 46),),
    'color': ((199, 213, 207),(195, 205, 207),(143, 159, 170),(178, 175, 191),(182, 184, 195),(255, 255, 255),(129, 137, 154),),
  },
  'CombatVictory': {
    'pos': ((364, 113),(485, 120),(618, 113),(438, 449),(397, 463),(448, 477),),
    'color': ((255, 255, 255),(242, 242, 243),(245, 245, 246),(127, 112, 41),(194, 195, 201),(127, 80, 0),)
  },
  'CombatVictory2': {
    'pos': ((364, 111),(419, 117),(484, 119),(618, 109),(396, 465),(436, 449),(446, 477),),
    'color': ((255, 255, 255),(255, 255, 255),(248, 249, 249),(244, 244, 244),(255, 255, 255),(127, 112, 41),(127, 80, 0),)
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

LastStage = '_'
def is_stage(stg):
  global LastStage
  s = get_current_stage()
  if s != LastStage:
    _G.log_info("Current stage:", s)
    LastStage = s
  return s and stg in s
