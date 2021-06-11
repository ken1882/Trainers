import _G, stage
import UmaData.common
import UmaData.MihonoBorubon
from random import randint
from _G import log_debug, log_error, log_info, log_warning

# How many weight added to objective per difference
AttrDistanceWeightPlus = [
  0.01,
  0.01,
  0.01,
  0.01,
  0.01,
]

# Weight for each suppor card present
SupporterWeightMultiplier = 1.0

# Objective prehead calculating when determine attribute weight
ObjectiveDepth = 2

# When prehead calc, attribute weight decay per depth
ObjectiveWeightDecay = 0.8

# Post-calc of y = λx + σ
ObjectiveWeightLambda = 1.0
ObjectiveWeightSigma  = 0

def init():
  for module in dir(UmaData):
    if module[:2] == '__':
      continue
    if _G.CurrentUmaName == module:
      _G.CurrentUma = getattr(UmaData, module)
      break

def get_objective_weight(depth=0):
  obj_idx = min(len(_G.CurrentUma.ObjectiveAttributeMin)-1, _G.NextObjectiveIndex+depth)
  attr_distance = []
  for idx,attr in enumerate(_G.CurrentUma.ObjectiveAttributeMin[obj_idx]):
    attr_distance.append(max(0, attr - _G.CurrentAttributes[idx]))
  
  log_info(f"Attr diff: {attr_distance}")
  attr_weight = []
  for idx,dis in enumerate(attr_distance):
    attr_weight.append( dis * AttrDistanceWeightPlus[idx] * (ObjectiveWeightDecay**depth))
  return attr_weight

def determine_training_objective(sup_num=[0,0,0,0,0],attr_inc=[0,0,0,0,0]):
  '''
  * sup_num -- Support cards present in each training
  * attr_inc -- Unused
  '''
  attr_weight      = [n * SupporterWeightMultiplier for n in sup_num]
  objective_weight = [0,0,0,0,0]
  for depth in range(ObjectiveDepth+1):
    if depth + _G.NextObjectiveIndex >= len(_G.CurrentUma.ObjectiveAttributeMin):
      break
    weights = get_objective_weight(depth)
    objective_weight = [sum(n) for n in zip(objective_weight,weights)]
    log_info(f"Objective weight: {weights}")

  
  attr_weight = [sum(n) for n in zip(attr_weight,objective_weight)]
  log_info(f"Attribute training weight: {attr_weight}")
  return attr_weight.index( max(attr_weight) )
  
def determine_event_selection(event_data):
  event_name,event_options = event_data
  if event_name in _G.CurrentUma.PreferredEventOption:
    ret = _G.CurrentUma.PreferredEventOption[event_name]
    log_info(f"Preferred option:{ret}")
    return ret
  
  ret = randint(0,len(event_options)-1)
  log_info(f"Randomly choosed option: {ret}")
  return ret

def determine_next_main_action():
  energy = stage.get_energy()
  sicked = stage.is_healthroom_available()