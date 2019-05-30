import G, const, stage, action, util, Input
from G import uwait

FlagInit = False
CurrentTurn = 0

def initialize():
  global FlagInit, CurrentTurn
  FlagInit = True
  CurrentTurn = 0

def is_battle_ready():
  return G.FlagGrindLevel and G.RepairOKTimestamp < G.CurTime

def deploy_pos():
  return const.TeamDeployPos[G.GrindLevel]

def process_battle_start():
  yield from action.deploy_troops()
  action.start_battle()

def process_in_turn():
  global CurrentTurn
  yield from action.move_troop(G.GrindLevel, CurrentTurn)
  end_turn()

def end_turn():
  global CurrentTurn
  CurrentTurn += 1
  action.end_turn()

def update():
  if not is_battle_ready():
    return
  if stage.is_stage_combat_map():
    if FlagInit:
      G.normal_update()
      G.ActionFiber = process_battle_start()
      return
    else:
      G.ActionFiber = process_in_turn()
  elif stage.is_stage_enemy_turn():
    pass
  elif stage.is_stage_victory():
    pass
  else:
    action.random_click(*const.BattleNextPos)
  
def process_turns():
  global Fiber
  pass