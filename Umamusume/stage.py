import cv2
import numpy as np
from win32con import MAXSTRETCHBLTMODE
import _G
import graphics, position
from util import (wait, uwait, img2str, ocr_rect)
from desktopmagic.screengrab_win32 import getRectAsImage
from _G import (log_debug, log_error, log_info, log_warning)

CVMatchThreshold = 0.6  # Similarity rate thresholf
CVMatchMinCount  = 2    # How many matched point need to pass
TrainingEffectStat = (
  (0,2,5),    # speed, power, skill pt(all)
  (1,3,5),    # stamina, willness
  (1,2,5),    # stamina, power
  (0,2,3,5),  # speed, power, willness
  (0,4,5)     # speed, wisdom
)

Enum = {
  'TrainMain': {
    'id': 1,
    'color': ((253, 250, 211),(231, 81, 82),(74, 207, 225),(90, 181, 57)),
    'pos': ((116, 779),(357, 782),(528, 822),(534, 163)),
  },
  'TrainSummer': {
    'id': 2,
    'pos': ((82, 759),(93, 762),(102, 761),(357, 782),(523, 823),(406, 937),),
    'color': ((255, 252, 242),(228, 82, 82),(255, 252, 242),(231, 81, 82),(74, 207, 225),(253, 113, 162),)
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

def validate_train_effect(menu_index, numbers):
  if menu_index == 0:   # speed
    if max(numbers) != numbers[0] or numbers[1] < numbers[2]:
      return False
  elif menu_index == 1: # stamina
    if max(numbers) != numbers[0] or numbers[1] < numbers[2]:
      return False
  elif menu_index == 2: # power
    if max(numbers) != numbers[1] or numbers[0] < numbers[2]:
      return False
  elif menu_index == 3: # willness
    if max(numbers) != numbers[2] or numbers[0] < numbers[3]:
      return False
  elif menu_index == 4: # wisdom
    if max(numbers) != numbers[1] or numbers[2] < numbers[0]:
      return False
  return True

def get_all_training_effect():
  pass

def get_training_effect(menu_index):
  global CVMatchThreshold, CVMatchMinCount, TrainingEffectStat
  size   = len(TrainingEffectStat[menu_index])
  passed = False
  while not passed:
    effect = []
    idx    = 0
    while idx < size:
      graphics.flush()
      rect = position.TrainingIncreaseRect[TrainingEffectStat[menu_index][idx]]
      fname = f"training{idx}.png"
      graphics.take_snapshot(rect, fname)
      wait(0.3)
      src = cv2.imread(f"{_G.DCTmpFolder}/{fname}")
      dig_x = {}
      digit = []
      ar_ok_cnt = []
      ar_ok_pos = {}
      max_match = 0
      for i in range(10):
        dig_x[i] = 0
        ar_ok_pos[i] = []
        tmp = cv2.imread(_G.UmaNumberImage[i])
        res = cv2.matchTemplate(src, tmp, cv2.TM_CCOEFF_NORMED)
        matched = np.where(res >= CVMatchThreshold)
        ok_cnt  = 0
        sum_x   = 0
        for y,x in zip(*matched):
          ok_cnt += 1
          sum_x  += x
          ar_ok_pos[i].append((x,y))
          max_match = max(max_match, ok_cnt)
        dig_x[i] = sum_x
        ar_ok_cnt.append(ok_cnt)
        ar_ok_pos[i] = sorted(ar_ok_pos[i], key=lambda _pos: _pos[0])
      
      for n in range(10):
        last_x = -1
        if ar_ok_cnt[n] < max_match:
          continue
        for pos in ar_ok_pos[n]:
          if pos[0] - last_x > 10:
            digit.append(n)
          last_x = pos[0]
      
      digit = sorted(digit, key=lambda v:dig_x[v])
      log_info(f"Training benefit#{idx}:\nok count: {ar_ok_cnt}\ndigits: {digit}\ndigit x: {dig_x}\npos: {ar_ok_pos}")
      try:
        number = int("".join([str(d) for d in digit]))
      except (TypeError,ValueError):
        number = 0
      if number >= 2 and number <= 100:
        effect.append(number)
        idx += 1
    passed = validate_train_effect(menu_index, effect)
    if not passed:
      log_info(f"Wrong OCR training effect ({effect}), retry")
  return effect 
  