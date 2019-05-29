import G, const, stage, action, util, Input
from G import uwait

FlagInit = False
Fiber = None

def initialize():
  global FlagInit
  FlagInit = True

def is_battle_ready():
  return G.FlagGrindLevel and G.RepairOKTimestamp < G.CurTime

def deploy_pos():
  return const.TeamDeployPos[G.GrindLevel]

def update():
  global Fiber
  if not is_battle_ready():
    return
  if stage.is_stage_combat_map():
    if FlagInit:
      G.normal_update()
      G.ActionFiber = action.deploy_troops()
      return
    else:
      if Fiber:
        alive = util.resume(Fiber)
        if not alive:
          Fiber = None
          action.random_click(*const.BattleStartPos)
  elif stage.is_stage_victory():
    pass
  else:
    action.random_click(*const.BattleNextPos)
  
def process_turns():
  global Fiber
  pass