import G, const, util, action, stage, Input
from G import uwait

def update():
  if stage.is_stage_pudding():
    if stage.is_pudding_token_enough():
      action.enter_level()
    else:
      print("No enough token!")
      G.FlagRunning = False
  return True
