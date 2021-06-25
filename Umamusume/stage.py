from copy import copy
from time import sleep

import cv2
import numpy as np
from desktopmagic.screengrab_win32 import getRectAsImage

import _G
import corrector
import graphics
import Input
import position
import util
from _G import log_debug, log_error, log_info, log_warning, resume, uwait, wait
from _G import CVMatchHardRate,CVMatchMinCount,CVMatchStdRate,CVLocalDistance
from util import img2str, isdigit, ocr_rect

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
    'pos': ((8, 18),(121, 18),(179, 14),(240, 340),(376, 337),(539, 277),),
    'color': ((72, 68, 92),(99, 93, 126),(252, 249, 249),(156, 211, 41),(156, 211, 41),(247, 249, 247),),
  },
  'RaceSelection': {
    'id': 4,
    'pos': ((167, 870),(29, 464),(352, 849),(252, 883),(546, 393),(35, 991),),
    'color': ((121, 64, 22),(255, 127, 132),(165, 223, 5),(255, 255, 255),(247, 248, 247),(255, 255, 255),),
  },
  'ObjectiveComplete': {
    'id': 5,
    'pos': ((153, 297),(234, 294),(307, 297),(420, 296),(297, 894),),
    'color': ((200, 255, 35),(206, 255, 45),(198, 255, 27),(205, 255, 40),(255, 255, 255),)
  },
  'RaiseComplete': {
    'id': 6,
    'pos': ((8, 18),(131, 12),(429, 374),(360, 278),(366, 589),(75, 830),(78, 863),(177, 820),(327, 877),(484, 834),),
    'color': ((72, 68, 92),(99, 93, 126),(255, 166, 72),(121, 216, 35),(121, 216, 35),(247, 247, 250),(53, 203, 221),(27, 149, 55),(248, 80, 140),(49, 120, 189),)
  },
  'ObjectivePrepare': {
    'id': 7,
    'pos': ((18, 87),(78, 863),(99, 894),(224, 899),(177, 856),(536, 163),(471, 813),),
    'color': ((255, 255, 255),(244, 243, 247),(41, 193, 214),(68, 203, 222),(27, 149, 55),(90, 181, 57),(239, 42, 41),)
  },
  'RacePrepare': {
    'id': 8,
    'pos': ((362, 153),(356, 364),(359, 466),(358, 525),(437, 957),(261, 966),(170, 683),),
    'color': ((121, 216, 35),(121, 216, 35),(121, 216, 35),(121, 216, 35),(154, 218, 4),(255, 255, 255),(255, 255, 255),)
  },
  'Inheritance': {
    'id': 9,
    'pos': ((230, 842),(261, 844),(301, 840),(324, 853),(351, 840),),
    'color': ((255, 250, 195),(255, 243, 180),(255, 251, 208),(255, 227, 123),(255, 251, 208),)
  },
  'RaceResult': {
    'id': 10,
    'pos': ((44, 25),(56, 31),(195, 933),(371, 960),(554, 1012),(24, 56),),
    'color': ((88, 181, 57),(88, 181, 57),(159, 220, 5),(140, 207, 0),(235, 234, 239),(255, 199, 0),)
  },
  'Event': { # Support Event
    'id': 11,
    'pos': ((89, 180),(89, 193),(8, 198),(9, 181),(430, 222),),
    'color': ((71, 199, 250),(49, 146, 244),(46, 141, 245),(74, 192, 247),(112, 202, 255),)
  },
  'Event2': { # Charactor Event
    'id': 12,
    'pos': ((6, 206),(5, 182),(92, 195),(428, 221),(262, 170),),
    'color': ((253, 101, 162),(255, 150, 165),(253, 105, 162),(255, 186, 206),(255, 162, 173),)
  },
  'Event3': { # Story Event
    'id': 13,
    'pos': ((6, 180),(7, 225),(82, 180),(82, 224),(431, 221),),
    'color': ((159, 226, 11),(99, 199, 20),(165, 228, 16),(101, 203, 22),(165, 235, 77),)
  },
  'Event4': { # Character Custom Event
    'id': 12,
    'pos': ((5, 183),(5, 203),(90, 227),(258, 172),(472, 226),),
    'color': ((255, 150, 165),(253, 101, 162),(255, 101, 165),(255, 162, 173),(255, 188, 206),)
  },
  'Event5': {
    'id': 13,
    'pos': ((6, 177),(4, 205),(92, 221),(91, 195),(442, 194),),
    'color': ((255, 150, 165),(253, 101, 163),(253, 105, 162),(253, 105, 162),(255, 192, 209),)
  },
  'ObjectiveRetry': {
    'id': 14,
    'pos': ((172, 264),(498, 448),(75, 720),(322, 727),(512, 754),(558, 687),(305, 612),),
    'color': ((126, 204, 11),(238, 230, 227),(255, 253, 255),(154, 218, 8),(151, 215, 5),(250, 251, 250),(236, 231, 228),)
  },
  'NoticeRaceExhaustion': {
    'id': 15,
    'pos': ((14, 332),(302, 329),(57, 501),(520, 544),(76, 651),(339, 665),),
    'color': ((101, 186, 0),(255, 255, 255),(88, 181, 57),(254, 254, 254),(255, 255, 255),(143, 212, 8),)
  },
}

Status = {
  'pos': (480, 117),
  # color
  'color': (
    # 絕不調(0) ~ 絕好調(4)
    (201, 128, 255), (13, 174, 247), (255, 212, 24), (255, 170, 63), (255, 131, 156)
  ),
  'name': ('絕不調','不調','普通','好調','絕好調')
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

SkillSelNextPageScroll = ((552,627),(526,143))

HealthRoom = {
  'pos': ((79, 902),(183, 933),(189, 905),),
  'color': ((244, 243, 247),(170, 121, 247),(236, 235, 239),)
}

SkillBarBottomPos = (563, 814) 
SkillBarBottomColor = (118,116,134)
GetSkillPos = (241, 859)
GetSkillColor = (154,218,8)

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

def get_skill_points(is_race):
  filename = f"skpt.png"
  graphics.take_snapshot(position.RaceSkillPtRect if is_race else position.SkillPtRect, filename)
  sleep(0.3)
  res = img2str(filename)
  try:
    return abs(int(res))
  except ValueError:
    log_warning(f"Unable to convert OCR result `{res}` to int")
  return 0

def get_status():
  global Status
  rgb = graphics.get_pixel(*Status['pos'])
  for i,c in enumerate(Status['color']):
    if graphics.is_color_ok(rgb,c):
      return i 
  return StatusBest

def get_date():
  fname = 'date.png'
  try:
    return corrector.date(ocr_rect(position.DateRect, fname, 1.0).strip())
  except Exception as err:
    log_warning("Unable to get date:", err)
    return -1

def get_race_fans():
  f0 = ocr_rect(position.RaceFanRect1, 'racefan1.png', 2.0).strip()
  wait(1)
  f1 = ocr_rect(position.RaceFanRect2, 'racefan2.png', 2.0).strip()
  return [util.str2int(f0), util.str2int(f1)]

def validate_train_effect(menu_index, numbers):
  """
  Validate training attributes increase whether legal.
  * (int) menu_index -- From left to right, the index of training objective
  * (int[6]) numbers -- Attributes increased, i.e. [SPD,STA,POW,WIL,WIS,SKP]
  """
  return True # might broken due to sickness
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
  '''
  Get all training effects, i.e. attributes increase
  * (bool) only_support: Only get number of supports present and ignore attributes
  '''
  ret  = []
  ret2 = []
  for i,pos in enumerate(position.AttrTrainPos):
    speed = 20 if i == 0 else 10
    Input.moveto(*pos, speed)
    wait(0.5 if only_support else 3)
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
  '''
  Get number support cards present in current training objective
  '''
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
  '''
  Get attributes increase amount of training.
  * (int 0~4) menu_index: From left to right, the index of training objective
  '''
  global CVMatchStdRate, CVMatchMinCount, CVLocalDistance, TrainingEffectStat
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
      _G.flush()
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
          if pos[1] - last_x >= CVLocalDistance:
            max_sim = 0
          if match_result[n][pos] > max_sim:
            ar.append(pos)
            max_sim = match_result[n][pos]
        ar_ok_pos[n] = copy(ar)

      # treat as another digit if match point not close to each other
      for n in range(10):
        last_x = -CVLocalDistance
        if depth < 3 and (ar_ok_cnt[n] == 0 or max(ar_ok_cnt[n]+2,ar_ok_cnt[n]*1.4) < max_match):
          continue
        elif ar_ok_cnt[n] < CVMatchMinCount:
          continue
          
        for pos in ar_ok_pos[n]:
          if pos[1] - last_x >= CVLocalDistance:
            if n == 1:    # 1 and 4
              flag_greater = True
              for pos2 in ar_ok_pos[4]:
                if abs(pos2[1] - pos[1]) < CVLocalDistance and match_result[4][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            elif n == 4:  # 1 and 4
              flag_greater = True
              for pos2 in ar_ok_pos[1]:
                if abs(pos2[1] - pos[1]) < CVLocalDistance and match_result[1][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            elif n == 3:  # 3 and 8
              flag_greater = True
              for pos2 in ar_ok_pos[8]:
                if abs(pos2[1] - pos[1]) < CVLocalDistance and match_result[8][pos2] > match_result[n][pos]:
                  flag_greater = False
                  break
              if flag_greater:
                digit.append(n)
            elif n == 8:  # 3 and 8
              flag_greater = True
              for pos2 in ar_ok_pos[3]:
                if abs(pos2[1] - pos[1]) < CVLocalDistance and match_result[3][pos2] > match_result[n][pos]:
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
      log_info(f"OCR result: {number}")
      if number >= 0 and number <= 100:
        effect[TrainingEffectStat[menu_index][idx]] = number
        idx += 1
    passed = validate_train_effect(menu_index, effect)
    if not passed:
      log_info(f"Wrong OCR training effect ({effect}), retry")
  return effect 
  
def get_event_data():
  fname = 'event.png'
  raw   = ocr_rect(position.EventTitleRect, fname, zoom=1.2).split('  ')[0].replace(' ','')
  event_names = list(_G.UmaEventData.keys())
  rates = [util.diff_string(raw,ename) for ename in event_names]
  event_name = event_names[rates.index(max(rates))]
  log_info(f"`{raw}` => `{event_name}`")
  return (event_name, _G.UmaEventData[event_name])


def get_attributes(skpt=True,is_race=False): # include skill points
  '''
  * skpt: Include skill points
  '''
  ret = []
  for idx,rect in enumerate(position.RaceAttributesRect if is_race else position.AttributesRect):
    try:
      attr_raw = ocr_rect(rect, f"attr{idx}.png")
      attr = abs(util.str2int(attr_raw))
      if attr > 1200: # possible misrecognization
        attr %= 1000
      ret.append(attr)
    except Exception:
      ret.append(0)
  if skpt:
    ret.append(get_skill_points(is_race))
  return ret

def _ocr_available_skills(immediate=False,to_get=[]):
  ret = []
  up_pos  = graphics.find_object(_G.ImageSkillUp, threshold=0.95)
  up_pos2 = graphics.find_object(_G.ImageSkillUp2, threshold=0.95)
  available_points = up_pos + up_pos2
  log_info("Skillup template local max:", available_points)
  checked = []
  for idx,pxy in enumerate(available_points):
    px,py    = pxy
    px = int(px)
    py = int(py)
    rsx,rsy  = int(px - 400), int(py - 24) # skill name rect
    rex,rey  = int(px - 250), int(py + 4)
    name_raw = ocr_rect((rsx,rsy,rex,rey), f"skill{idx}.png", zoom=1.2, lang='jpn')
    cost_raw = ocr_rect((px-56,py+8,px-12,py+34), f"cost{idx}.png", lang='eng')
    fixed    = corrector.skill_name(name_raw)
    cost     = corrector.skill_cost(cost_raw)
    log_info("Skill cost:", cost)
    if fixed in checked:
      log_info("Skill already checked, skip")
      continue
    checked.append(fixed)
    if (fixed in to_get) or (immediate and fixed in _G.CurrentUma.ImmediateSkills):
      Input.moveto(px+15,py+15)
      uwait(0.3)
      Input.click()
      uwait(0.3)
      if fixed[-1] == '◎':
        flag_lvled = False
        for sk in _G.CurrentOwnedSkills:
          if sk[0][:-1] == fixed[:-1]:
            flag_lvled = True
            break
        if not flag_lvled:
          fixed = fixed[:-1] + '○'
      _G.CurrentOwnedSkills.append((fixed,cost))
      _G.CurrentAttributes[5] -= cost
      log_info(f"Learned skill {fixed}; points left: {_G.CurrentAttributes[5]}")
      if (_G.CurrentAttributes[5] < _G.MinGetSkillPoints) or (fixed in to_get and to_get.index(fixed) == len(to_get) - 1):
        return _G.MsgPipeStop
    else:
      ret.append((fixed, cost))
  return ret

def get_available_skills(_async,immediate=False,to_get=[]):
  '''
  Get available skill to obtain
  * `_async` -- Run function in a fiber/generator
  * `immediate=False` -- Will spend points to get `ImmediateSkills` as soon as it's available and won't returned, \
    wanrning that `_G.CurrentAttributes[5]` (skill points) will be reduced here.
  * `to_get=[]` -- Skill names to get
  '''
  ret = []
  flag_duped = False  
  while not flag_duped:
    if _async:
      yield
    else:
      _G.flush()
    skills = _ocr_available_skills(immediate, to_get)
    if skills == _G.MsgPipeStop:
      break
    for s in skills:
      if s not in ret:
        ret.append(s)
      else:
        flag_duped = True
    # break if duped or to bottom
    if flag_duped:
      break
    if graphics.is_color_ok(graphics.get_pixel(*SkillBarBottomPos, True), SkillBarBottomColor):
      break
    sx,sy = SkillSelNextPageScroll[0]
    ex,ey = SkillSelNextPageScroll[1]
    Input.moveto(sx,sy)
    Input.scroll_to(sx,sy,ex,ey)
    uwait(1)

  if _async:
    yield (_G.MsgPipeRet, ret)
  else:
    return ret
  
def get_race_ranking():
  mrate = 0.2
  ret   = 0
  for idx,fname in enumerate(_G.ImageRaceRanking):
    pts,rts = graphics.find_object_with_rates(fname, 0.98)
    if pts and rts[0] > mrate:
      ret = idx+1
      mrate = rts[0]
  return ret

def is_healthroom_available():
  return graphics.is_pixel_match(HealthRoom['pos'], HealthRoom['color'])

def has_obtained_skill():
  return graphics.is_color_ok(graphics.get_pixel(*GetSkillPos, True), GetSkillColor)

def is_common_race(race):
  if race['Date'][0] == 'ファイナルズ 開催中':
    return True
  if race['Date'][0] == 'ジュニア級デビュー前':
    return True
  return False