import util, action, stage, const
import numpy as np

FlagFrozen = False
LastPixels = np.array([])
cnt_timeout = 0

def is_frozen():
  return FlagFrozen

def get_freeze_timer():
  return cnt_timeout

def detect_freeze():
  global LastPixels, cnt_timeout, FlagFrozen
  pixels = []
  for pos in const.FrozenDetectorPixel:
    pixels.append(util.getPixel(*pos))
  if np.array_equal(LastPixels, np.array(pixels)):
    cnt_timeout += 1
    if cnt_timeout > 40:
      FlagFrozen = True
  else:
    FlagFrozen  = False
    cnt_timeout = 0
  LastPixels = np.array(pixels)

def reset():
  global FlagFrozen, cnt_timeout
  FlagFrozen  = False
  cnt_timeout = 0