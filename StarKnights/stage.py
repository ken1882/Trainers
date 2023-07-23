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
    'pos': ((937, 19),(111, 704),(651, 281),(561, 268),(499, 270),),
    'color': ((8, 16, 66),(255, 130, 255),(255, 255, 255),(255, 255, 255),(255, 255, 255),)
  },
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

def is_stage(stg):
  s = get_current_stage()
  return s and stg in s

if __name__ == '__main__':
  while True:
    if Input.is_trigger(win32con.VK_NUMPAD0, True):
      break
    if Input.is_trigger(win32con.VK_NUMPAD1, True):
        print(graphics.get_mouse_pixel())