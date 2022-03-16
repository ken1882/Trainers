from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait
import Input, position, heuristics, training, tourment
from random import randint

def start_test_fiber():
  heuristics.init()
  _G.flush()
  yield
  try:
    print("Energy:", stage.get_energy())
    print("Status:", stage.Status['name'][stage.get_status()])
    print("Date:", stage.get_date())
    stg = stage.get_current_stage()
    print("Stage:", stg)
    if not stg:
      return
    if 'Event' in stg:
      edata = stage.get_event_data() # name,options
      print("Event:", edata[0])
      oindex = heuristics.determine_event_selection(edata)
      # Input.rmoveto(*position.EventOption[len(edata[1])][oindex])
      # uwait(0.3)
      # Input.click()
    if stg == 'ObjectivePrepare':
      print("Attrs:", stage.get_attributes(is_race=True))
    if stg == 'RaceResult':
      print("Race ranking:", stage.get_race_ranking())
    if stg != 'TrainMain' and stg != 'TrainSummer':
      return
    
    attrs = stage.get_attributes()
    print("Attributes:", attrs)
    _G.CurrentAttributes = attrs[:5]
    Input.rmoveto(*position.TrainMenu)
    Input.click()
    uwait(1)
    stat,sup = stage.get_all_training_effect(True)
    print(f"Stat add: {stat}\nSupports: {sup}")
    tindex = heuristics.determine_training_objective(sup)
    print(f"Train index: {tindex}")
    uwait(0.3)
    # Input.rmoveto(*position.AttrTrainPos[tindex+1])
    # Input.dclick()
    
  except InterruptedError:
    pass

def start_train_fiber():
  yield from resume_from(training.start())


def start_tourment_fiber():
  yield from tourment.start()

def start_teamrace_fiber():
  times = int(_G.ARGV.repeats)
  while True:
    uwait(0.3)
    stg = stage.get_current_stage()
    yield
    if not stg:
      continue
    if 'TeamRaceTitle' in stg:
      Input.rmoveto(*position.TeamRaceEnter)
      uwait(0.3)
      Input.click()
      yield
    elif 'TeamRaceOpponent' in stg:
      Input.rmoveto(*position.TeamRaceOpponent)
      uwait(0.3)
      Input.click()
    elif 'TeamRaceList' in stg:
      Input.rmoveto(*position.TeamRaceStart)
      uwait(0.3)
      Input.click()
      for _ in range(5):
        uwait(0.1)
        yield
      Input.rmoveto(*position.TeamRaceConfirm)
      uwait(0.3)
      Input.click()
    elif 'TeamRaceSkipAll' in stg:
      Input.rmoveto(*position.TeamRaceNext)
      uwait(0.3)
      Input.click()
      for _ in range(3):
        uwait(0.5)
        Input.rmoveto(*position.TeamRaceSkipResult)
        uwait(0.3)
        Input.click()
    elif 'TeamRaceAllResult' in stg:
      Input.rmoveto(*position.TeamRaceAllResultOk)
      uwait(0.3)
      Input.click()
    elif 'TeamRaceSchedule' in stg:
      while stg and ('TeamRaceAward' not in stg or 'TeamRaceResult' not in stg):
        yield
        stg = stage.get_current_stage()
        Input.rmoveto(*position.TeamRaceSkip)
        uwait(0.3)
        Input.click()
    elif 'TeamRaceAward' in stg:
      Input.rmoveto(*position.TeamRaceNext)
      uwait(0.3)
      Input.click()
      for _ in range(5):
        uwait(0.2)
        yield
      Input.rmoveto(*position.TeamRaceNext)
      uwait(0.1)
      Input.click()
    elif 'TeamRaceResult' in stg:
      Input.rmoveto(*position.TeamRaceResultOk)
      uwait(0.3)
      Input.click()
      times -= 1
      if times <= 0:
        break