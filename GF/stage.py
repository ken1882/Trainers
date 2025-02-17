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
  'PartyEdit': {
    'pos': ((87, 32),(85, 48),(21, 23),(137, 38),(175, 52),(230, 31),(259, 34),(373, 38),(130, 442),(941, 128),(980, 471),),
    'color': ((255, 255, 255),(255, 255, 255),(39, 39, 39),(255, 255, 255),(255, 255, 255),(248, 248, 248),(165, 165, 165),(165, 165, 165),(48, 48, 48),(14, 55, 72),(50, 50, 50),),
  },
  'PartyMemberEdit': {
    'pos': ((19, 17),(137, 38),(196, 33),(278, 39),(342, 40),(439, 47),(925, 369),(948, 371),(979, 408),(867, 314),),
    'color': ((40, 40, 40),(255, 255, 255),(49, 49, 49),(253, 179, 0),(49, 49, 49),(141, 141, 141),(255, 255, 255),(49, 50, 49),(50, 50, 50),(49, 50, 49),)
  },
  'BattleSelection': {
    'pos': ((21, 28),(217, 30),(239, 51),(289, 43),(311, 42),(343, 32),(85, 503),(117, 491),),
    'color': ((32, 36, 38),(255, 255, 255),(255, 255, 255),(159, 159, 159),(165, 165, 165),(50, 50, 50),(114, 112, 119),(160, 161, 162),),
  },
  'BattleSelectionConfirm': {
    'pos': ((182, 74),(222, 73),(425, 79),(574, 88),(790, 481),(851, 438),(674, 139),),
    'color': ((157, 157, 157),(255, 255, 255),(255, 255, 255),(30, 30, 30),(253, 179, 0),(124, 90, 0),(81, 81, 80),),
  },
  'CombatPlayerTurnEnd': {
    'pos': ((34, 27),(87, 29),(231, 25),(268, 26),(27, 468),(42, 538),(317, 14),(774, 520),(787, 534),(799, 519),(787, 505),(808, 517),(821, 534),(835, 519),(820, 504),(858, 487),),
    'color': ((154, 154, 155),(255, 255, 255),(253, 80, 1),(255, 255, 255),(255, 255, 255),(240, 2, 79),(31, 31, 32),(254, 170, 6),(254, 170, 6),(254, 170, 6),(254, 170, 6),(254, 170, 6),(254, 170, 7),(254, 170, 7),(254, 170, 6),(254, 243, 2),)
  },
  'CombatPlayerPhase': {
    'pos': ((15, 20),(32, 25),(75, 31),(232, 25),(316, 22),(42, 389),(52, 382),(55, 541),(964, 516),(880, 490),),
    'color': ((154, 154, 155),(154, 154, 155),(255, 255, 255),(253, 80, 1),(31, 31, 31),(202, 16, 50),(1, 18, 22),(54, 47, 47),(253, 180, 1),(255, 233, 3),),
  },
  'CombatPrepare': {
    'pos': ((19, 17),(32, 24),(66, 26),(345, 43),(360, 43),(312, 21),(42, 389),(120, 465),(63, 541),(816, 496),(931, 501),(956, 503),),
    'color': ((154, 154, 155),(154, 154, 155),(255, 255, 255),(131, 131, 131),(197, 197, 197),(31, 31, 32),(202, 16, 50),(255, 255, 255),(54, 47, 47),(56, 67, 75),(49, 50, 50),(253, 180, 2),),
  },
  'CombatPrepare2': {
    'pos': ((36, 543),(123, 539),(28, 467),(42, 389),(27, 36),(75, 29),(181, 31),(380, 14),(352, 59),),
    'color': ((240, 2, 79),(54, 46, 47),(255, 255, 255),(202, 16, 50),(154, 154, 155),(255, 255, 255),(255, 255, 255),(31, 31, 31),(255, 255, 255),)
  },
  'CombatPartySelect': {
    'pos': ((149, 44),(133, 80),(159, 76),(286, 77),(136, 401),(529, 484),(733, 491),(811, 498),(873, 501),(917, 508),(149, 476),(261, 484),(984, 101),),
    'color': ((254, 254, 254),(254, 254, 254),(254, 254, 254),(255, 255, 255),(210, 224, 92),(49, 49, 49),(50, 50, 50),(234, 234, 234),(50, 50, 50),(253, 179, 0),(254, 125, 0),(49, 49, 49),(14, 55, 72),),
  },
  'CombatFighting': {
    'pos': ((470, 12),(513, 13),(492, 11),(500, 14),(501, 9),(467, 7),(517, 7),),
    'color': ((253, 179, 0),(253, 179, 0),(255, 255, 255),(250, 240, 207),(252, 188, 31),(253, 179, 0),(253, 179, 0),),
  },
  'CombatFightingEnd': {
    'pos': ((148, 400),(739, 294),(735, 305),(135, 47),(141, 35),(16, 511),(845, 451),),
    'color': ((227, 227, 227),(255, 255, 255),(255, 255, 255),(255, 255, 255),(217, 216, 215),(86, 86, 86),(255, 255, 255),),
  },
  'CharacterObtained': {
    'pos': ((77, 24),(70, 27),(63, 30),(54, 32),(62, 38),(70, 43),(47, 46),(37, 27),(90, 32),(93, 45),),
    'color': ((254, 254, 254),(255, 255, 255),(255, 255, 255),(255, 255, 255),(171, 170, 170),(254, 254, 254),(73, 73, 73),(75, 75, 75),(75, 75, 75),(75, 75, 75),),
  },
  'CombatPartyPanel': {
    'pos': ((132, 83),(151, 44),(266, 74),(984, 99),(892, 422),(728, 496),(861, 503),(955, 484),(262, 482),),
    'color': ((254, 254, 254),(254, 254, 254),(255, 255, 255),(14, 55, 72),(237, 212, 0),(234, 234, 234),(50, 50, 50),(255, 255, 255),(49, 49, 49),),
  },
  'CombatFullInventory': {
    'pos': ((244, 277),(271, 319),(290, 373),(339, 403),(518, 307),(543, 353),(544, 403),(744, 408),(754, 346),),
    'color': ((33, 33, 33),(89, 89, 89),(11, 11, 11),(2, 221, 255),(144, 144, 144),(33, 33, 33),(253, 179, 0),(253, 179, 0),(33, 33, 33),),
  },
  'SceneFactory': {
    'pos': ((80, 41),(136, 21),(138, 52),(156, 47),(174, 56),(170, 31),(236, 23),(213, 49),(238, 59),(265, 39),(291, 41),(345, 30),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(206, 206, 206),(145, 146, 147),(190, 190, 191),(253, 253, 253),(165, 165, 165),(145, 146, 146),(50, 50, 50),)
  },
  'SceneFactory2': {
    'pos': ((79, 39),(138, 30),(176, 54),(235, 54),(238, 30),(264, 33),(308, 43),(190, 19),(210, 53),(287, 27),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(253, 253, 253),(253, 253, 253),(165, 165, 165),(165, 165, 165),(90, 91, 91),(253, 253, 253),(165, 165, 165),)
  },
  'LogisticsComplete': {
    'pos': ((22, 20),(25, 34),(122, 38),(141, 41),(171, 25),(202, 39),(219, 30),(241, 41),(832, 525),(918, 518),(918, 531),(949, 514),),
    'color': ((222, 222, 222),(221, 222, 222),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(253, 179, 0),(253, 179, 0),(255, 255, 255),(253, 179, 1),),
  },
  'HomeMenu': {
    'pos': ((9, 92),(398, 19),(541, 26),(981, 9),(819, 14),(532, 521),(532, 526),(632, 521),(850, 530),(948, 299),(967, 319),(664, 326),(680, 357),(684, 217),),
    'color': ((3, 134, 199),(255, 255, 255),(255, 255, 255),(244, 171, 2),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),(49, 49, 49),(247, 179, 13),(49, 49, 49),(255, 255, 192),(243, 244, 246),),
  },
  # '': {
  #   'pos': [],
  #   'color': [],
  # },
  # '': {
  #   'pos': [],
  #   'color': [],
  # },
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

def get_disks():
  ret = []
  for i,rect in enumerate(position.DiskNames):
    name = utils.ocr_rect(rect, f'disk#{i}.png', lang='eng', config='--psm 12 --psm 13 -c tessedit_char_whitelist=ACENYaceghlr')
    name = [ch if re.match(r'\w',ch) else '' for ch in name]
    name = ''.join(name)
    if utils.diff_string(_G.DiskTypes[0], name) > 0.75:
      ret.append(_G.DiskTypes[0])
    elif utils.diff_string(_G.DiskTypes[2], name) > 0.75:
      ret.append(_G.DiskTypes[2])
    else:
      ret.append(_G.DiskTypes[1])
  return ret

def get_current_formation():
  ret = []
  for i,pixstr in enumerate(position.BattlerPosition):
    if i == 0 or pixstr['pos'] == (0,0):
      continue
    if check_pixels(pixstr):
      ret.append(i)
  return ret

def get_connection_targets():
  ret = []
  for i,pos in enumerate(position.ConnectionPos):
    if i == 0:
      continue
    if graphics.is_color_ok(graphics.get_pixel(*pos, True), position.ConnectionColor):
      ret.append(i)
  return ret