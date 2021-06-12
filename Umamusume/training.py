from types import prepare_class
from corrector import skill_cost
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
    if scene == 'TrainMain' or scene == 'TrainSummer':
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
    uwait(4)
    return
  if actions[0] == _G.ActionPlay:
    Input.rmoveto(*position.GoOut)
    uwait(0.3)
    Input.click()
    _G.CurrentAction = _G.ActionPlay
    uwait(4)
    return
  if actions[0] == _G.ActionRest:
    Input.rmoveto(*position.Rest)
    uwait(0.3)
    Input.click()
    _G.CurrentAction = _G.ActionRest
    uwait(4)
    return
  if actions[0] == _G.ActionRace:
    if _G.CurrentAttributes[5] > _G.MinGetSkillPoints: # skill points
      Input.rmoveto(*position.SkillSelection)
      Input.click()
      yield from get_skills()
      uwait(0.3)
      Input.rmoveto(*position.CommonReturnPos)
      Input.click()
      uwait(1)
    else:
      log_info(f"Not enough points to learn skill ({_G.CurrentAttributes[5]})")
      
  if actions[0] == _G.ActionTrain:
    _G.CurrentAction = _G.ActionTrain
    
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
    uwait(4)
    return

def process_objective():
  obj_name = _G.CurrentUma.ObjectiveName[_G.NextObjectiveIndex]
  log_info("Processing objective:", obj_name)
  _G.CurrentAction = _G.ActionObjective
  attrs = stage.get_attributes(is_race=True)
  _G.CurrentAttributes = attrs
  log_info("Attributes:", attrs)
  if attrs[5] > _G.MinGetSkillPoints: # skill points
    Input.rmoveto(*position.PreObjectiveSkillPos)
    uwait(0.3)
    yield
    Input.click()
    yield from get_skills()
    uwait(0.3)
    Input.rmoveto(*position.CommonReturnPos)
    Input.click()
    uwait(1)
  else:
    log_info(f"Not enough points to learn skill ({_G.CurrentAttributes[5]})")
  Input.rmoveto(*position.PreObjectiveRacePos)
  Input.click()
  yield from select_race(_G.UmaRaceData[obj_name])
  while not stage.get_current_stage() == 'RacePrepare':
    uwait(1)
    _G.flush()
    yield
  yield from race_processing()

def get_skills():
  while not stage.get_current_stage() == 'SkillSelection':
    uwait(1)
    yield
  fiber = stage.get_available_skills(True, True)
  while resume(fiber):
    yield
  skills = _G.pop_fiber_ret()
  log_info("Skills available:", skills)
  
  if _G.CurrentAttributes[5] > _G.MinGetSkillPoints:
    log_info("Checking skills to learn, points left:", _G.CurrentAttributes[5])
    obtains = heuristics.determine_skills2get(skills)
    learnable = []
    for sn in obtains:
      for name,cost in skills:
        if name != sn:
          continue
        if cost < _G.CurrentAttributes[5]:
          continue
        _G.CurrentAttributes[5] -= cost
        learnable.append(name)
    log_info("Skills to learn:", learnable)
    if learnable:
      Input.moveto(*position.SkillBarTopPos)
      Input.mouse_down()
      uwait(0.5)
      Input.mouse_up()
      uwait(0.8)
      log_info("Start learning skills")
      fiber = stage.get_available_skills(True, to_get=learnable)
      while resume(fiber):
        yield
      _G.pop_fiber_ret()
    log_info("Skill learning complete")
  else:
    log_info(f"Not enough points to learn skill ({_G.CurrentAttributes[5]})")
  
  if stage.has_obtained_skill():
    Input.rmoveto(*position.GetSkillPos)
    Input.click()
    uwait(0.3)
    Input.rmoveto(*position.ConfirmSkillPos)
    Input.click()
    uwait(3)
    Input.rmoveto(*position.CloseSkillPos)
    Input.click()
    uwait(0.3)

def select_race(target):
  while not stage.get_current_stage() == 'RaceSelection':
    uwait(1)
    _G.flush()
    yield
  f1, f2 = stage.get_race_fans()
  mx,my = 0,0
  if f1 == target['Fans'] or target['Date'][0] == 'ファイナルズ 開催中':
    mx = (position.RaceFanRect1[0] + position.RaceFanRect1[2]) // 2
    my = (position.RaceFanRect1[1] + position.RaceFanRect1[3]) // 2
  elif f2 == target['Fans']:
    mx = (position.RaceFanRect2[0] + position.RaceFanRect2[2]) // 2
    my = (position.RaceFanRect2[1] + position.RaceFanRect2[3]) // 2
  if mx == 0 or my == 0:
    raise RuntimeError("No corresponding race data found!")
  _G.CurrentRaceData = target
  Input.rmoveto(mx, my)
  Input.click()
  uwait(0.3)
  Input.moveto(*position.RaceJoinPos)
  Input.click()
  uwait(0.3)
  Input.moveto(*position.ConfirmRacePos)
  Input.click()

def race_processing():
  Input.rmoveto(*position.SeeRaceResultPos)
  Input.click()
  for _ in range(10):
    uwait(0.5)
    yield
  while not stage.get_current_stage() == 'RaceResult':
    Input.rmoveto(*position.CommonNext)
    Input.click()
    _G.flush()
    uwait(1)
    yield
  ranking = stage.get_race_ranking()
  ranking_str = str(ranking)+'着' if ranking > 0 else '着外'
  log_info("Race ended, ranking:", ranking_str)