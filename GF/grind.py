import G, const, stage, action, util, Input
from G import uwait

FlagInit = False
FlagStartEngaging = False
MovementFiber = None
Fiber = None
CurrentTurn = 0
EngagingMovementFlags = []
EngagingStartTime = 0

def initialize():
  global FlagInit, CurrentTurn
  FlagInit = True
  CurrentTurn = 0

def is_battle_ready():
  return G.FlagGrindLevel and G.RepairOKTimestamp < G.CurTime

def deploy_pos():
  return const.TeamDeployPos[G.GrindLevel]

def process_battle_start():
  global FlagInit
  yield from action.deploy_troops()
  action.start_battle()
  yield from action.supply_team()

def next_until_ok():
  while stage.is_stage_combat_event() and not stage.is_stage_combat_map() or not stage.is_stage_loading() and not stage.is_stage_combat_selection():
    action.combat_next()
    yield

def process_victory():
  global Fiber, MovementFiber
  MovementFiber = None
  yield from next_until_ok()
  print("Combat ends")
  G.FlagRepairNeeded = True
  G.FlagSwapTeamNeeded = True
  G.RepairOKTimestamp = 9223372036854775807

def process_movements():
  global CurrentTurn
  yield from action.move_troop(G.GrindLevel, CurrentTurn)
  end_turn()

def end_turn():
  global CurrentTurn
  CurrentTurn += 1
  action.end_turn()

def update():
  global MovementFiber, FlagInit, Fiber
  if Fiber:
    if util.resume(Fiber):
      print("Resume grind normal fiber")
    else:
      Fiber = None
      print("Grind normal fiber finished")
  if MovementFiber:
    return update_in_turn_actions()
  
  if not is_battle_ready():
    return
  elif stage.is_stage_combat_map():
    if FlagInit:
      print("Battle start")
      G.normal_update()
      G.ActionFiber = process_battle_start()
      FlagInit = False
      return
    else:
      MovementFiber = process_movements()
  elif stage.is_stage_enemy_turn():
    pass
  elif stage.is_stage_victory():
    Fiber = process_victory()
  else:
    action.random_click(*const.BattleNextPos)


def update_in_turn_actions():
  global Fiber, MovementFiber, FlagStartEngaging, EngagingMovementFlags, EngagingStartTime
  if stage.is_stage_engaging():
    if not FlagStartEngaging:
      FlagStartEngaging = True
      EngagingStartTime = util.get_current_time_sec()
      EngagingMovementFlags = []
    else:
      for i, move in enumerate(const.TeamEngagingMovement[G.GrindLevel][G.CurrentTeamID]):
        if util.get_current_time_sec() + move[0] < EngagingStartTime:
          continue
        if i in EngagingMovementFlags:
          continue
        EngagingMovementFlags.append(i)
        action.random_scroll_to(*move[1])
  elif stage.is_stage_loading():
    return
  elif stage.is_stage_victory():
    Fiber = process_victory()
  elif stage.is_stage_neutralized() or stage.is_stage_combat_event():
    Fiber = next_until_ok()
    FlagStartEngaging = False
  elif stage.is_stage_combat_map():
    print("Resume movement fiber")
    if not util.resume(MovementFiber):
      print("Movement fiber finished")
      MovementFiber = None