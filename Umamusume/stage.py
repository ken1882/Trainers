import cv2
import numpy as np
from win32con import MAXSTRETCHBLTMODE
import _G
import graphics, position, Input
from util import (img2str, ocr_rect)
from desktopmagic.screengrab_win32 import getRectAsImage
from _G import (log_debug,log_error,log_info,log_warning,resume,wait,uwait)
from time import sleep
from copy import copy

CVMatchStdRate = 1.0      # Similarity standard deviation ratio above average in consider digit matched
CVMatchMinCount  = 1      # How many matched point need to pass
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
  'pos': (473, 118),
  # color
  'color': (
    # 絕不調(0) ~ 絕好調(4)
    (0,0,0), (16, 135, 247), (255, 212, 24), (255, 170, 63), (255, 131, 156)
  )
}
StatusBest    = 4
StatusGood    = 3
StatusNormal  = 2
StatusBad     = 1
StatusWorst   = 0

ColorNoEnergy = (118,117,118)
EnergyBarRect = (184, 131, 405, 132)
HealRoomPos = (80,908)
HealRoomColor = (154,150,157)

SupportAvailablePos = (
  (545,228), (545,325), (545,422), (545,518), (545,615)
)
SupportAvailableColor = ((110,107,121),(253, 172, 31),(251, 231, 120))

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
  sleep(0.3)
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
    if max(numbers) != numbers[0] or numbers[2] < numbers[5]:
      return False
  elif menu_index == 1: # stamina
    if max(numbers) != numbers[1] or numbers[3] < numbers[5]:
      return False
  elif menu_index == 2: # power
    if max(numbers) != numbers[2] or numbers[1] < numbers[5]:
      return False
  elif menu_index == 3: # willness
    if max(numbers) != numbers[3] or numbers[3] < numbers[0]:
      return False
  elif menu_index == 4: # wisdom
    if max(numbers) != numbers[4] or numbers[5] < numbers[0]:
      return False
  return True

def get_all_training_effect(only_support=False):
  ret  = []
  ret2 = []
  for i,pos in enumerate(position.StateCheckPos):
    speed = 20 if i == 0 else 10
    Input.moveto(*pos, speed)
    wait(3)
    if i == 0:
      Input.mouse_down()
    else:
      if not only_support:
        res = get_training_effect(i-1)
        ret.append(res)
      ret2.append(get_training_supports())
  Input.mouse_up()
  return [ret,ret2]

def get_training_supports():
  global SupportAvailablePos,SupportAvailableColor
  cnt = 0
  for pos in SupportAvailablePos:
    rgb = graphics.get_pixel(*pos,True)
    if any([graphics.is_color_ok(rgb,col) for col in SupportAvailableColor]):
      cnt += 1
    else:
      break
  return cnt

def get_training_effect(menu_index):
  global CVMatchStdRate, CVMatchMinCount, TrainingEffectStat
  size   = len(TrainingEffectStat[menu_index])
  passed = False
  while not passed:
    effect = [0,0,0,0,0,0] # SPD,STA,POW,WIL,WIS,SKP
    idx    = 0
    lidx   = -1
    depth  = 0
    while idx < size:
      depth = 0 if lidx != idx else depth
      depth += 1
      lidx = idx
      graphics.flush()
      rect = position.TrainingIncreaseRect[TrainingEffectStat[menu_index][idx]]
      fname = f"training{idx}.png"
      graphics.take_snapshot(rect, fname)
      wait(0.3)
      src = cv2.imread(f"{_G.DCTmpFolder}/{fname}")
      dig_x = {}      # matched digit average of x-coord
      digit = []      # matched digits
      ar_ok_cnt = []  # matched digit count
      ar_ok_pos = {}  # matched digit position
      max_match = 0   # Max match points of a digit
      max_similarity = []
      match_result = []
      for i in range(10):
        dig_x[i] = 0
        ar_ok_pos[i] = []
        tmp = cv2.imread(_G.UmaNumberImage[i])
        res = cv2.matchTemplate(src, tmp, cv2.TM_CCOEFF_NORMED)
        match_result.append(res)
        max_similarity.append(np.max(res))
      threshold = np.average(max_similarity) + np.std(max_similarity) * CVMatchStdRate
      for i in range(10):
        matched = np.where(match_result[i] >= threshold)
        ok_cnt  = 0
        x_poses = []
        for y,x in zip(*matched):
          ok_cnt += 1
          x_poses.append(x)
          ar_ok_pos[i].append((y,x))
          max_match = max(max_match, ok_cnt)
        dig_x[i] = np.average(x_poses)
        ar_ok_cnt.append(ok_cnt)
        ar_ok_pos[i] = sorted(ar_ok_pos[i], key=lambda _pos: _pos[1])
      

      # filter to only local maximum left
      for n in range(10):
        ar = []
        last_x = -10
        max_sim = 0
        for pos in ar_ok_pos[n]:
          if pos[1] - last_x >= 10:
            max_sim = 0
          if match_result[n][pos] > max_sim:
            ar.append(pos)
            max_sim = match_result[n][pos]
        ar_ok_pos[n] = copy(ar)

      # treat as another digit if match point not close to each other
      for n in range(10):
        last_x = -10
        if depth < 3 and (ar_ok_cnt[n] == 0 or max(ar_ok_cnt[n]+2,ar_ok_cnt[n]*1.4) < max_match):
          continue
        elif ar_ok_cnt[n] < CVMatchMinCount:
          continue
        for pos in ar_ok_pos[n]:
          if pos[1] - last_x >= 10:
            if n == 1:
              flag_greater = True
              for pos2 in ar_ok_pos[4]:
                if abs(pos2[1] - pos[1]) < 10 and match_result[4][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            elif n == 4:
              flag_greater = True
              for pos2 in ar_ok_pos[1]:
                if abs(pos2[1] - pos[1]) < 10 and match_result[1][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            elif n == 3:
              flag_greater = True
              for pos2 in ar_ok_pos[8]:
                if abs(pos2[1] - pos[1]) < 10 and match_result[8][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            elif n == 8:
              flag_greater = True
              for pos2 in ar_ok_pos[3]:
                if abs(pos2[1] - pos[1]) < 10 and match_result[3][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            else:
              digit.append(n)
          last_x = pos[1]
      
      # get final number by x-coord match point
      digit = sorted(digit, key=lambda v:dig_x[v])
      log_info(f"Training benefit#{idx}/{depth}:\nthreshold: {threshold}\nsim. rate: {max_similarity}\nok count: {ar_ok_cnt}\ndigits: {digit}\ndigit x: {dig_x}\npos: {ar_ok_pos}")
      try:
        number = int("".join([str(d) for d in digit]))
      except (TypeError,ValueError):
        number = 0
      if number >= 2 and number <= 100:
        effect[TrainingEffectStat[menu_index][idx]] = number
        idx += 1
    passed = validate_train_effect(menu_index, effect)
    if not passed:
      log_info(f"Wrong OCR training effect ({effect}), retry")
  return effect 
  
def get_event_title():
  fname = 'event.png'
  return ocr_rect(position.EventTitleRect, fname, zoom=1.2).translate(str.maketrans('。',' ')).strip()