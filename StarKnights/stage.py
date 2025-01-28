from copy import copy
from time import sleep
import win32con

import _G
import graphics
import Input
import utils
from _G import log_debug, log_error, log_info, log_warning, resume, uwait, wait
from _G import CVMatchHardRate,CVMatchMinCount,CVMatchStdRate,CVLocalDistance
from utils import img2str, isdigit, ocr_rect
import re

Enum = {
  'CombatResult': {
    'pos': ((1254, 675),(1211, 651),(658, 647),(43, 171),(43, 236),(122, 637),(56, 656),),
    'color': ((243, 219, 53),(243, 237, 118),(222, 215, 88),(233, 237, 240),(234, 238, 242),(77, 181, 231),(226, 228, 232),)
  },
  'CombatVictory': {
    'pos': ((665, 54),(738, 107),(907, 107),(1145, 54),(1231, 119),),
    'color': ((255, 169, 82),(255, 255, 161),(255, 255, 161),(255, 169, 82),(255, 255, 129),)
  },
  'CombatRewards': {
    'pos': ((412, 190),(453, 227),(566, 187),(715, 227),(886, 227),(866, 184),),
    'color': ((255, 170, 82),(255, 255, 171),(255, 167, 82),(255, 255, 171),(255, 255, 171),(255, 167, 82),)
  },
  'CombatInitiate': {
    'pos': ((639, 561),(759, 271),(750, 703),(841, 359),),
    'color': ((255, 255, 255),(255, 255, 255),(68, 215, 189),(255, 255, 255),)
  },
  'CombatInitiate2': {
    'pos': ((576, 271),(438, 361),(841, 361),(102, 698),(1268, 698),(1240, 61),),
    'color': ((255, 255, 255),(255, 255, 255),(255, 255, 255),(255, 153, 255),(24, 162, 255),(33, 51, 129),)
  },
  'CombatInitiate3': {
    'pos': ((884, 13),(90, 12),(106, 704),(1268, 696),(1255, 51),(1238, 60),(638, 547),(648, 283),(639, 172),),
    'color': ((255, 182, 247),(255, 105, 137),(255, 129, 255),(24, 162, 255),(219, 240, 239),(32, 49, 124),(255, 255, 255),(255, 255, 255),(255, 255, 255),)
  },
  'EventBoss': {
    'pos': ((149, 644),(51, 659),(137, 627),(1028, 672),(954, 638),),
    'color': ((255, 105, 137),(255, 255, 255),(247, 0, 99),(82, 53, 35),(129, 186, 253),)
  },
  'NewScene': {
    'pos': ((211, 86),(1038, 74),(242, 639),(932, 639),(631, 623),(329, 302),),
    'color': ((255, 255, 255),(148, 158, 175),(214, 230, 254),(225, 236, 247),(252, 253, 254),(181, 235, 255),)
  },
  'EventReward': {
    'pos': ((867, 227),(1037, 156),(578, 518),(262, 557),(261, 162),(393, 382),(141, 623),),
    'color': ((90, 157, 214),(147, 158, 175),(252, 253, 254),(209, 228, 253),(198, 223, 253),(90, 157, 214),(124, 2, 63),)
  },
  'KakinAd': {
    'pos': ((990, 530),(1239, 563),(1010, 617),(1063, 668),(1178, 71),),
    'color': ((255, 36, 167),(255, 36, 167),(243, 237, 118),(82, 53, 35),(245, 245, 245),)
  }
}

def get_current_stage():
  global Enum
  for key in Enum:
    stg = Enum[key]
    if graphics.is_pixel_match(stg['pos'], stg['color'], sync=True):
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

if __name__ == '__main__':
  while True:
    if Input.is_trigger(win32con.VK_NUMPAD0, True):
      break
    if Input.is_trigger(win32con.VK_NUMPAD1, True):
        print(graphics.get_mouse_pixel())