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
  'CharacterSelection': {
    'pos': ((793, 38),(44, 85),(47, 162),(46, 241),(44, 320),(45, 398),(43, 475),(73, 1020),),
    'color': ((1, 5, 14),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),)
  },
  'CharacterSelection2': {
    'pos': ((45, 87),(45, 164),(45, 240),(1866, 146),(749, 43),(72, 1021),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(62, 53, 40),(173, 219, 239),)
  },
  'SceneMap': {
    'pos': ((812, 1000),(971, 999),(1678, 989),(1712, 985),(1848, 1043),),
    'color': ((28, 83, 4),(7, 77, 108),(136, 102, 68),(119, 34, 34),(130, 103, 58),)
  },
  'SceneMap2': {
    'pos': ((16, 1067),(1903, 186),(1673, 971),(1696, 975),(1735, 977),(1829, 972),),
    'color': ((57, 52, 57),(17, 16, 14),(204, 102, 85),(219, 118, 101),(183, 149, 83),(187, 68, 34),)
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

def is_stage(stg):
  s = get_current_stage()
  return s and stg in s

def check_pixels(pixstruct):
  return graphics.is_pixel_match(pixstruct['pos'], pixstruct['color'])

def get_distance(fallback=None):
  ss = utils.ocr_rect(position.DistanceRect, fname='dist.png', whitelist='y.0123456789')
  ret = utils.str2float(ss)
  return fallback if ret == None else ret

def get_coord(force_correct=False, depth=0, interval=3):
  ss = utils.ocr_rect(position.CoordRect, fname='coord.png', whitelist='XYZ:.0123456789')
  _G.log_info(ss)
  sp = ss.split(':')
  ret = []
  if len(sp) == 4:
    ret = [utils.str2float(f) % 100 for f in sp[1:]]
  else:
    buffer = ''
    for ch in ss:
      if ch in '0123456789.':
        buffer += ch
        # if len(buffer) >= 6:
        #   ret.append(utils.str2float(buffer) % 100)
        #   buffer = ''
      elif buffer:
        ret.append(utils.str2float(buffer) % 100)
        buffer = ''
    if buffer:
      ret.append(utils.str2float(buffer) % 100)
      buffer = ''
  if force_correct and len(ret) != 3:
    _G.log_info(f"Wrong coord format: {ret}, retry (depth={depth+1})")
    if depth > 3:
      _G.log_warning("Returning probably wrong coord")
      return ret
    uwait(interval)
    _G.flush()
    return get_coord(True, depth+1, interval)
  return ret

def has_targeted_object():
  return graphics.is_pixel_match(
    ((678, 85),(685, 86),(702, 86),(712, 86),),
    ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),)
  )

def get_craft_progress():
  res = utils.ocr_rect(
    position.CraftProgress,
    'cr_prog.png',
    lang='eng',
    whitelist='0123546789/.',
    zoom=1.5,
    binarization=110,
    trim=True
  )
  print(res)
  res = [utils.str2int(n) for n in res.split('/')]
  return res

def get_craft_durability():
  res = utils.ocr_rect(
    position.CraftDurability,
    'cr_dur.png',
    lang='eng',
    whitelist='0123546789/.',
    zoom=2,
    binarization=100,
    trim=True
  )
  print(res)
  res = [utils.str2int(n) for n in res.split('/')]
  return res

def is_cp_recoverable():
  return graphics.is_color_ok(
    graphics.get_pixel(*position.TottPosCol[0], True),
    position.TottPosCol[1]
  )

def is_durability_recoverable():
  return graphics.is_color_ok(
    graphics.get_pixel(*position.CRMMPosCol[0], True),
    position.CRMMPosCol[1]
  )

def is_mooch_available():
  return graphics.is_color_ok(
    graphics.get_pixel(*position.MoochPosCol[0], True),
    position.MoochPosCol[1]
  )

def is_thaliak_available():
  return graphics.is_color_ok(
    graphics.get_pixel(*position.ThaliakPosCol[0], True),
    position.ThaliakPosCol[1]
  )

def is_gp_full():
  return not graphics.is_color_ok(
    graphics.get_pixel(*position.FishFullGPPosCol[0], True),
    position.FishFullGPPosCol[1]
  )

def is_gp_half():
  return not graphics.is_color_ok(
    graphics.get_pixel(*position.FishHalfGPPosCol[0], True),
    position.FishHalfGPPosCol[1]
  )

def is_max_hq():
  return graphics.is_color_ok(
    graphics.get_pixel(*position.CRHQPosCol[0], True),
    position.CRHQPosCol[1]
  )

def is_player_targeted():
  return graphics.is_pixel_match(*position.OtherPlayerPosCol, sync=True)

def is_enemy_targeted():
  return is_enemy_awared() or graphics.is_pixel_match(*position.UnawareEnemyPosCol, sync=True)

def is_enemy_awared():
  for pix, col in position.ActiveEnemyPosCols:
    if graphics.is_pixel_match(pix, col, sync=True):
      return True
  return False