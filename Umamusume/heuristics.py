import corrector
import _G, stage, corrector
import UmaData.common
from random import randint
from _G import log_debug, log_error, log_info, log_warning
from UmaData.common import get_skill_rstyle
from glob import glob
import importlib

files = glob("UmaData/*.py")
for file in files:
  lib = file.replace('/', '.').replace('\\', '.')[:-3]
  log_info(f"Import {lib}")
  importlib.import_module(lib)

def init():
  for module in dir(UmaData):
    if module[:2] == '__':
      continue
    if _G.CurrentUmaName == module:
      _G.CurrentUma = getattr(UmaData, module)
      break
  cur_date = stage.get_date()
  _G.NextObjectiveIndex = 0
  _G.CurrentOwnedSkills = []
  _G.CurrentRaceData    = None
  for date,name in list(_G.CurrentUma.DateOptionalRace.items()):
    if type(date) == int:
      continue
    intdate = corrector.date(date)
    _G.CurrentUma.DateOptionalRace[intdate] = name
    log_info(f"Date Race translated {date} => {intdate} ({name})")
  if cur_date:
    for date in _G.CurrentUma.ObjectiveDate:
      if cur_date > corrector.date(date,False):
        _G.NextObjectiveIndex += 1
  _G.NextObjectiveIndex = min(len(_G.CurrentUma.ObjectiveDate)-1, _G.NextObjectiveIndex)
  log_info(f"Current date: {cur_date}, next objective: {_G.CurrentUma.ObjectiveDate[_G.NextObjectiveIndex]}")

def get_objective_weight(depth=0):
  obj_idx = min(len(_G.CurrentUma.ObjectiveAttributeMin)-1, _G.NextObjectiveIndex+depth)
  attr_distance = []
  for idx,attr in enumerate(_G.CurrentUma.ObjectiveAttributeMin[obj_idx]):
    attr_distance.append(max(0, attr - _G.CurrentAttributes[idx]))
  
  log_info(f"Attr diff: {attr_distance}")
  attr_weight = []
  for idx,dis in enumerate(attr_distance):
    w = dis * _G.CurrentUma.AttrDistanceWeightPlus[idx] * (_G.CurrentUma.ObjectiveWeightDecay**depth)
    attr_weight.append(w)
  return attr_weight

def determine_training_objective(sup_num=[0,0,0,0,0],attr_inc=[0,0,0,0,0]):
  '''
  * sup_num -- Support cards present in each training
  * attr_inc -- Unused
  '''
  attr_weight      = [n * _G.CurrentUma.SupporterWeightMultiplier for n in sup_num]
  objective_weight = [0,0,0,0,0]
  # pre-calc objectives
  for depth in range(_G.CurrentUma.ObjectiveDepth+1):
    if depth + _G.NextObjectiveIndex >= len(_G.CurrentUma.ObjectiveAttributeMin):
      break
    weights = get_objective_weight(depth)
    objective_weight = [sum(n) for n in zip(objective_weight,weights)]
    log_info(f"Objective weight: {weights}")
  
  # attribute training weight calculation
  attr_weight = [sum(n) for n in zip(attr_weight,objective_weight)]
  obj_idx = min(len(_G.CurrentUma.ObjectiveAttributeMin)-1, _G.NextObjectiveIndex)
  dd = corrector.date(_G.CurrentUma.ObjectiveDate[obj_idx]) - stage.get_date()
  log_info(f"Attribute weight: {attr_weight}")
  log_info(f"Next objective date left: {dd}")
  dd = max(0,dd-2)
  for idx,attr in enumerate(_G.CurrentAttributes[:5]):
    mul   = 1.0
    decay = _G.CurrentUma.ObjectiveWeightDecay
    if attr < _G.CurrentUma.ObjectiveAttributeMin[obj_idx][idx]:
      mul = _G.CurrentUma.MinAttributeWeightMultiplier[idx]
    elif attr > _G.CurrentUma.ObjectiveAttributeFair[obj_idx][idx]:
      mul = _G.CurrentUma.OverAttributeWeightMultiplier[idx]
    else:
      mul = _G.CurrentUma.FairAttributeWeightMultiplier[idx]
    mul = mul * (decay ** dd)
    attr_weight[idx] *= mul
  log_info(f"Attribute training weight: {attr_weight}")
  return attr_weight.index( max(attr_weight) )
  
def determine_event_selection(event_data):
  event_name,event_options = event_data
  if len(event_options) <= 1:
    return 0

  if event_name in _G.CurrentUma.PreferredEventOption:
    ret = _G.CurrentUma.PreferredEventOption[event_name]
    log_info(f"Preferred option:{ret}")
    return ret
  
  ret = randint(0,len(event_options)-1)
  log_info(f"Randomly choosed option: {ret}")
  return ret

def get_optional_race(date):
  if date in _G.CurrentUma.DateOptionalRace:
    return _G.UmaRaceData[_G.CurrentUma.DateOptionalRace[date]]
  for race_name in _G.CurrentUma.OptionalRace:
    if any([corrector.date(dat,False) == date for dat in _G.UmaRaceData[race_name]['Date']]):
      return _G.UmaRaceData[race_name]
  return None

def determine_next_main_action():
  energy = stage.get_energy()
  sicked = stage.is_healthroom_available()
  date   = stage.get_date()
  status = stage.get_status()
  race   = get_optional_race(date)
  _G.CurrentStatus = status
  _G.CurrentDate = date
  _G.CurrentAttributes = stage.get_attributes()
  log_info("Energy:", energy)
  log_info("Status:", stage.Status['name'][status])
  log_info("Date:", date)
  log_info("Sicked:", sicked)
  log_info("Attributes:", _G.CurrentAttributes)

  if race:
    _flag_ok = True
    log_info("Attributes to next objective:")
    for idx,attr in enumerate(_G.CurrentUma.ObjectiveAttributeMin[_G.NextObjectiveIndex]):
      d = max(0, corrector.date(_G.CurrentUma.ObjectiveDate[_G.NextObjectiveIndex]) - date - 2)
      w = attr * (_G.CurrentUma.MinAttributeDateWeightDecay[idx] ** d)
      print(f"{_G.CurrentAttributes[idx]} / {attr} => {w} {_G.CurrentAttributes[idx] < w}")
      if _G.CurrentAttributes[idx] < w:
        _flag_ok = False
        break
    if _flag_ok or _G.IgnoreStatLimit:
      return (_G.ActionRace, race)

  if sicked:
    return (_G.ActionHeal, None)
  
  if energy < 45:
    if date > 72: # ファイナルズ開催中
      return (_G.ActionTrain, 4)
    return (_G.ActionRest, None)
  
  if stage.get_current_stage() == 'TrainMain' and status < 4 and energy < 80:
    return (_G.ActionPlay, None)
  if stage.get_current_stage() == 'TrainSummer' and status < 4 and energy < 60:
    return (_G.ActionRest, None)

  return (_G.ActionTrain, None)

def determine_skills2get(skills):
  names = [s[0] for s in skills]
  costs = [s[1] for s in skills]
  points = _G.CurrentAttributes[5]
  ret = []
  log_info("Skill points:", points)
  for sk in UmaData.common.NormalSkillOrder:
    if points < 50: # unable to get more skills
      break
    if sk not in names or points < costs[names.index(sk)]:
      continue
    sk_rstyle = get_skill_rstyle(sk)
    if sk_rstyle != None and sk_rstyle != _G.CurrentUma.RunningStyle:
      continue
    ret.append(sk)
    points -= costs[names.index(sk)]
  return ret  
  
def should_learn_skill(date):
  pts = _G.CurrentAttributes[5]
  if date == 0 or date > 50:
    return pts > _G.MaxGetSkillPoints
  return pts > _G.MinGetSkillPoints