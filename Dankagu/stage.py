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
  'SongSelect2': {
    'pos': ((37, 17),(552, 45),(640, 17),(980, 15),(877, 47),(828, 401),(875, 397),(869, 548),),
    'color': ((243, 239, 223),(97, 84, 77),(97, 84, 77),(243, 239, 223),(235, 240, 240),(57, 38, 13),(97, 84, 77),(255, 219, 87),)
  },
  'PartySelect': {
    'pos': ((72, 539),(308, 541),(309, 558),(72, 564),(10, 17),(977, 14),(637, 187),(30, 320),(991, 317),),
    'color': ((77, 64, 56),(77, 64, 56),(243, 239, 223),(243, 239, 223),(243, 239, 223),(243, 239, 223),(97, 84, 77),(243, 239, 223),(243, 239, 223),)
  },
  'SongClear': {
    'pos': ((516, 104),(517, 146),(536, 309),(561, 298),(795, 310),(979, 455),(524, 411),),
    'color': ((242, 230, 208),(239, 237, 227),(255, 249, 241),(97, 84, 77),(223, 221, 219),(236, 230, 219),(241, 233, 224),)
  },
  'SongClear2': {
    'pos': ((538, 309),(546, 318),(545, 301),(591, 335),(647, 304),(700, 304),),
    'color': ((255, 250, 244),(97, 84, 77),(97, 84, 77),(247, 245, 239),(97, 84, 77),(223, 221, 219),)
  },
  'SceneLoading': {
    'pos': ((501, 266),(205, 240),(383, 173),(757, 185),(731, 380),(283, 303),(782, 226),(339, 207),),
    'color': ((0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),(0, 0, 0),)
  },
  'DayChanaged': {
    'pos': ((277, 204),(307, 250),(660, 242),(446, 354),(462, 365),(772, 382),(582, 367),(791, 206),),
    'color': ((227, 224, 211),(244, 241, 233),(247, 245, 239),(255, 181, 0),(255, 199, 17),(239, 235, 225),(255, 217, 88),(229, 226, 213),)
  },
  'LoginNotice': {
    'pos': ((102, 34),(435, 45),(493, 79),(94, 154),(93, 438),(467, 530),(799, 524),(933, 152),(888, 42),),
    'color': ((240, 238, 230),(215, 212, 196),(247, 245, 239),(245, 245, 237),(245, 245, 237),(240, 239, 226),(246, 244, 237),(244, 244, 236),(246, 244, 239),)
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
