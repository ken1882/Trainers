from mmap import ACCESS_WRITE

from numpy import ravel_multi_index
import _G,util,stage,graphics,Input,heuristics,position
from _G import resume_from,resume,wait,uwait,log_info,log_warning,log_debug,log_error

def start():
  heuristics.init()
  yield from main_loop()

def main_loop():
  while True:
    yield
    scene = stage.get_current_stage()
    if not scene:
      uwait(1)
      continue
    if scene == 'TrainMain':
      yield from next_main_action()
    elif scene == 'ObjectivePrepare':
      yield from process_objective()
    else:
      if 'Event' in scene:
        edata = stage.get_event_data() # name,options
        print("Event:", edata[0])
        oindex = heuristics.determine_event_selection(edata)
        Input.rmoveto(*position.EventOption[len(edata[1])][oindex])
        uwait(0.3)
        Input.click()
        uwait(2)

def next_main_action():
  actions = heuristics.determine_next_main_action()
  yield
  if actions[0] == _G.ActionHeal:
    Input.rmoveto(*position.Heal)
    uwait(0.3)
    Input.click()
    _G.CurrentAction = _G.ActionHeal
    uwait(2)
    return
  if actions[0] == _G.ActionPlay:
    Input.rmoveto(*position.GoOut)
    uwait(0.3)
    Input.click()
    _G.CurrentAction = _G.ActionPlay
    uwait(2)
    return
  if actions[0] == _G.ActionRest:
    Input.rmoveto(*position.Rest)
    uwait(0.3)
    Input.click()
    _G.CurrentAction = _G.ActionRest
    uwait(2)
    return
  if actions[0] == _G.ActionTrain:
    _G.CurrentAction = _G.ActionTrain
    attrs = stage.get_attributes()
    log_info("Attributes:", attrs)
    _G.CurrentAttributes = attrs[:5]
    
    Input.rmoveto(*position.TrainMenu)
    yield
    Input.click()
    uwait(1)
    yield
    
    tindex = 0
    if actions[1] == None:
      stat,sup = stage.get_all_training_effect(True)
      log_info(f"Stat add: {stat}\nSupports: {sup}")
      tindex = heuristics.determine_training_objective(sup)
      log_info(f"Train index: {tindex}")
      yield
    else:
      tindex = actions[1]
    uwait(0.3)
   
    Input.rmoveto(*position.AttrTrainPos[tindex+1])
    yield
    Input.dclick()
    uwait(2)
    return

def process_objective():
  _G.CurrentAction = _G.ActionObjective
  attrs = stage.get_attributes(is_race=True)
  if attrs[4] > 100:
    Input.rmoveto(*position.PreObjectiveSkillPos)
    uwait(0.3)
    yield
    Input.click()
    yield from get_skills()

def get_skills():
  pass