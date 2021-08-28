from os import stat
import collector
import _G,util,stage,graphics,Input,heuristics,position
from _G import resume_from,resume,wait,uwait,log_info,log_warning,log_debug,log_error

def start():
  util.ensure_dir_exist(f"{_G.DataCollectDirectory}/.csv")
  heuristics.init()
  yield from main_loop()

def main_loop():
  flag_has_event = False
  while True:
    yield
    scene = stage.get_current_stage()
    if not scene:
      uwait(1)
      continue
    if scene == 'TrainMain' or scene == 'TrainSummer':
      yield from next_main_action()
    if scene == 'RaiseComplete':
      log_info("Raising completed")
      break
    elif scene == 'ObjectivePrepare':
      yield from process_objective()
    elif scene == 'ObjectiveComplete':
      yield from process_objective_complete()
    elif scene == 'Inheritance':
      yield from process_inheritance()
    elif scene == 'RacePrepare':
      yield from process_race()
    elif scene == 'NotEnoughFans':
      Input.rmoveto(*position.NoFansCancelPos)
      uwait(0.3)
      Input.click()
    elif scene == 'ClawMiniGame':
      yield from process_minigame_claw()
    elif 'Event' in scene:
        if not flag_has_event:
          log_info("Event detected, waiting for 3 seconds")
          flag_has_event = True
          uwait(3)
          continue
        edata = stage.get_event_data() # name,options
        log_info("Event:", edata[0])
        oindex = heuristics.determine_event_selection(edata)
        flag_has_event = False
        Input.rmoveto(*position.EventOption[len(edata[1])][oindex])
        uwait(0.3)
        Input.click()
        if edata[0] == 'あんし〜ん笹針師、参☆上':
          uwait(1)
          Input.rmoveto(*position.EventOption[2][0])
          Input.click()
        uwait(3)
    if 'Event' not in scene:
      flag_has_event = False

def next_main_action():
  log_info("Processing main action")
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
    if heuristics.should_learn_skill(_G.CurrentDate):
      Input.rmoveto(*position.SkillSelection)
      Input.click()
      yield from get_skills()
      uwait(0.3)
      Input.rmoveto(*position.CommonReturnPos)
      Input.click()
      uwait(2)
    else:
      log_info(f"Not enough points to learn skill ({_G.CurrentAttributes[5]})")
    Input.rmoveto(*position.Race)
    uwait(0.3)
    Input.click()
    _G.CurrentRaceData = actions[1]
    yield from select_race(actions[1])
    uwait(3)
    yield from process_race()
      
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
  status = stage.get_status()
  attrs = stage.get_attributes(is_race=True)
  _G.CurrentStatus = status
  _G.CurrentAttributes = attrs
  log_info("Status:", status)
  log_info("Attributes:", attrs)
  if heuristics.should_learn_skill(_G.CurrentDate):
    Input.rmoveto(*position.PreObjectiveSkillPos)
    uwait(0.3)
    yield
    Input.click()
    yield from get_skills()
    uwait(0.3)
    Input.rmoveto(*position.CommonReturnPos)
    Input.click()
    uwait(3)
  else:
    log_info(f"Not enough points to learn skill ({_G.CurrentAttributes[5]})")
  Input.rmoveto(*position.PreObjectiveRacePos)
  uwait(0.3)
  Input.click()
  yield from select_race(_G.UmaRaceData[obj_name])
  uwait(3)
  yield from process_race()

def get_skills():
  log_info("Getting skills")
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
    log_info("Obtain skill order:", obtains)
    learnable = []
    for sn in obtains:
      for name,cost in skills:
        if name != sn:
          continue
        if cost > _G.CurrentAttributes[5]:
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
    while not stage.get_current_stage() == 'SkillLearningComplete':
      uwait(1)
      yield
    Input.rmoveto(*position.CloseSkillPos)
    Input.click()
    uwait(0.3)

def select_race(target):
  log_info("Selecting race")
  uwait(2)
  _G.flush()
  if stage.get_current_stage() == 'NoticeRaceExhaustion':
    Input.rmoveto(*position.ConfirmExRacePos)
    Input.click()
    uwait(1.5)
  while not stage.get_current_stage() == 'RaceSelection':
    uwait(1)
    _G.flush()
    yield
  
  flag_found = False
  for i in range(2):
    _G.flush()
    f1, f2 = stage.get_race_fans()
    log_info("Race fans:", f1, f2)
    mx = (position.RaceFanRect1[0] + position.RaceFanRect1[2]) // 2
    my = (position.RaceFanRect1[1] + position.RaceFanRect1[3]) // 2
    if f1 == target['Fans'] or stage.is_common_race(target):
      mx = (position.RaceFanRect1[0] + position.RaceFanRect1[2]) // 2
      my = (position.RaceFanRect1[1] + position.RaceFanRect1[3]) // 2
      flag_found = True
      break
    elif f2 == target['Fans']:
      mx = (position.RaceFanRect2[0] + position.RaceFanRect2[2]) // 2
      my = (position.RaceFanRect2[1] + position.RaceFanRect2[3]) // 2
      flag_found = True
      break
    if i == 1:
      break
    Input.moveto(*position.RaceSelectionScrollPos[0])
    uwait(0.3)
    Input.scroll_to(*position.RaceSelectionScrollPos[0],*position.RaceSelectionScrollPos[1], slow=True)
  if not flag_found:
    log_warning("No corresponding race found, processed to first choice")
  if stage.is_common_race(target):
    for rname in _G.CommonRaces:
      if _G.UmaRaceData[rname]['Fans'] == f1:
        target = _G.UmaRaceData[rname]
  _G.CurrentRaceData = target
  log_info("Race selected:", target['Name'])
  Input.rmoveto(mx, my)
  Input.click()
  uwait(0.3)
  Input.moveto(*position.RaceJoinPos)
  Input.click()
  uwait(0.3)
  Input.moveto(*position.ConfirmRacePos)
  Input.click()

def process_race():
  log_info("Process race")
  flag_race_finished = False
  retries = 0
  while not flag_race_finished:
    while not stage.get_current_stage() == 'RacePrepare':
      uwait(1)
      _G.flush()
      yield
    rstyle = stage.get_running_style()
    log_info(f"Strategy: {stage.RaceRunningStyle['name'][rstyle]}")
    if rstyle != _G.CurrentUma.RunningStyle:
      change_running_style()
      uwait(1)
      yield
      continue
    Input.rmoveto(*position.SeeRaceResultPos)
    Input.click()
    for _ in range(10):
      uwait(0.5)
      yield
    while True:
      stg = stage.get_current_stage()
      Input.rmoveto(*position.CommonNext)
      Input.click()
      _G.flush()
      uwait(1)
      yield
      if stg == 'RaceResult':
        flag_race_finished = True
        break
      elif stg == 'ObjectiveRetry':
        log_info("Objective failed, retry")
        Input.rmoveto(*position.ObjectiveRetryPos)
        wait(0.3)
        Input.click()
        retries += 1
        uwait(3)
        break
  ranking = stage.get_race_ranking()
  collector.record_race_result(_G.CurrentRaceData['Name'], ranking, retries)
  ranking_str = str(ranking)+'着' if ranking > 0 else '着外'
  log_info("Race ended, ranking:", ranking_str)
  Input.rmoveto(*position.RaceResultOkPos)
  Input.click()
  for _ in range(3):
    uwait(0.5)
    Input.rmoveto(*position.RaceResultNext, rrange=15)
    Input.click()
  for _ in range(3):
    uwait(0.5)
    Input.rmoveto(*position.RaceCompletePos, rrange=15)
    Input.click()

def change_running_style():
  Input.rmoveto(*position.ChangeRunningStylePos)
  uwait(0.3)
  Input.click()
  uwait(0.5)
  Input.rmoveto(*position.RaceRunningStylePos[_G.CurrentUma.RunningStyle])
  uwait(0.3)
  Input.click()
  uwait(0.3)
  Input.rmoveto(*position.ChangeRunningStyleOkPos)
  uwait(0.3)
  Input.click()
  uwait(1)

def process_objective_complete():
  log_info("Objective complete")
  for _ in range(4):
    uwait(1)
    Input.rmoveto(*position.CommonNext, rrange=15)
    Input.click()
    yield
  _G.NextObjectiveIndex += 1
  uwait(2)

def process_inheritance():
  log_info("Process inheritance")
  for _ in range(3):
    uwait(1)
    Input.rmoveto(*position.CommonNext, rrange=15)
    Input.click()
    yield

ClawForwardTime = (2, 1.1, 0.6)
def process_minigame_claw():
  mx,my = position.ClawMiniGamePos
  Input.rmoveto(mx, my-250)
  uwait(1)
  Input.click()
  uwait(0.3)
  Input.rmoveto(mx, my)
  uwait(0.3)
  for i,t in enumerate(ClawForwardTime):
    log_info(f"Minigame round {i+1}")
    Input.mouse_down()
    wait(t)
    Input.mouse_up()
    for _ in range(25-i*3):
      uwait(0.5)
      yield
  log_info("Minigame ended")
  uwait(2)
  Input.rmoveto(*position.ClawMiniGameEndPos)
  uwait(0.3)
  Input.click()
  uwait(2)
