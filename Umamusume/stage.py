import _G
import graphics, position
from util import (wait, uwait, img2str, ocr_rect)
from desktopmagic.screengrab_win32 import getRectAsImage
from _G import (log_debug, log_error, log_info, log_warning)

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
  'GoalComplete': {
    'id': 5,
    'pos': ((153, 297),(234, 294),(307, 297),(420, 296),(297, 894),),
    'color': ((200, 255, 35),(206, 255, 45),(198, 255, 27),(205, 255, 40),(255, 255, 255),)
  }
}

Status = {
  'pos': (477, 142),
  # color
  'color': (
    # 絕不調(0) ~ 絕好調(4)
    (0,0,0), (0,0,0), (0,0,0), (0,0,0), (247,71,128)
  )
}
StatusBest    = 4
StatusGood    = 3
StatusNormal  = 2
StatusBad     = 1
StatusWorst   = 0

ColorNoEnergy = (118,117,118)
EnergyBarRect = (184, 131, 405, 132)



def flush():
  _G.CurrentStage   = -1
  _G.LastFrameCount = -1

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

def get_skill_points():
  filename = f"skpt.png"
  graphics.take_snapshot(position.SkillPtRect, filename)
  uwait(0.3)
  res = img2str(filename)
  try:
    return int(res)
  except ValueError:
    log_warning(f"Unable to convert OCR result `{res}` to int")
  return 0

def get_status():
  global Status
  rgb = graphics.get_pixel(*Status['pos'])
  for i,c in enumerate(Status['color']):
    if rgb == c:
      return i 
  return StatusBest

def get_date():
  fname = 'date.png'
  return ocr_rect(position.DateRect, fname, 1.0).strip()

def get_race_fans():
  fname = 'racefan.png'
  f0 = ocr_rect(position.RaceFanRect1, fname, 2.0).strip()
  wait(1)
  f1 = ocr_rect(position.RaceFanRect2, fname, 2.0).strip()
  return [f0, f1]