import _G,stage

def start_test_fiber():
  try:
    print(stage.get_energy())
    print(stage.get_current_stage())
    print(stage.get_date())
    # stat,sup = stage.get_all_training_effect()
    # print(f"Stat add: {stat}\nSupports: {sup}")
    print(stage.get_training_effect(2))
  except InterruptedError:
    pass