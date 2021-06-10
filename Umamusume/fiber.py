from numpy import gradient
import _G,stage
from _G import resume, resume_from, pop_fiber_ret

def start_test_fiber():
  _G.flush()
  yield
  try:
    print("Energy:", stage.get_energy())
    print("Status:", stage.Status['name'][stage.get_status()])
    print("Date:", stage.get_date())
    stg = stage.get_current_stage()
    print("Stage:", stg)
    # stat,sup = stage.get_all_training_effect(True)
    # print(f"Stat add: {stat}\nSupports: {sup}")
    # print(stage.get_training_effect(2))
    # yield from resume_from(stage.get_available_skills(True))
    if 'Event' in stg:
      print("Event:", stage.get_event_title())
    if stg == 'TrainMain':
      print("Attributes:", stage.get_attributes())
    if stg == 'ObjectivePrepare':
      print("Stage:", stage.get_attributes(is_race=True))
    if stg == 'RaceResult':
      print("Race ranking:", stage.get_race_ranking())
    
  except InterruptedError:
    pass