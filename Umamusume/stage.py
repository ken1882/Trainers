import _G
import graphics
from PIL import Image

Enum = {
  'TrainMain': {
    'id': 1,
    'color': ((253, 250, 211),(231, 81, 82),(74, 207, 225),(90, 181, 57)),
    'pos': ((116, 779),(357, 782),(528, 822),(534, 163)),
  },
  'TrainSelection': {
    'id': 2,
    'pos': [],
    'color': [],
  },
  'SkillSelection': {
    'id': 3,
    'pos': [],
    'color': [],
  },
  'RaceSelection': {
    'id': 4,
    'pos': [],
    'color': [],
  },
}

ColorNoEnergy = (118,117,118)
EnergyBarRect = (184, 131, 405, 132)
LastFrameCount = -1

def get_current_stage():
  global Enum, LastFrameCount
  if LastFrameCount != _G.FrameCount:
    _G.CurrentStage = None
    LastFrameCount = _G.FrameCount
  elif _G.CurrentStage:
    return _G.CurrentStage
  
  for key in Enum:
    stg = Enum[key]
    if graphics.is_pixel_match(stg['pos'], stg['color']):
      _G.CurrentStage = key
      return key
  return None

def get_energy():
  ret = 0
  dx  = 2
  de  = 100.0 / (EnergyBarRect[2] - EnergyBarRect[0])
  cx,cy,_,_ = EnergyBarRect
  while cx < EnergyBarRect[2]:
    if graphics.get_pixel(cx,cy) == ColorNoEnergy:
      break
    cx  += dx
    ret += (de*dx)
  return ret 