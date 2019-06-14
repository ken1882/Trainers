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
  return G.RepairOKTimestamp < G.CurTime and G.GrindLevelCount > 0 and (G.FlagGrindLevel or G.FlagGrindEvent)

def deploy_pos():
  return const.TeamDeployPos[G.GrindLevel]

def process_battle_start():
  global FlagInit
  yield from action.deploy_troops()
  action.start_battle()

  if not G.FlagGrindEvent:
    if G.FlagSupplyNeeded:
      G.FlagSupplyNeeded = False
      yield from action.supply_team(0)
    yield from action.supply_team(1)

def next_until_ok():
  while stage.is_stage_combat_event() and not stage.is_stage_combat_map() or not stage.is_stage_loading() and not stage.is_stage_combat_selection():
    action.combat_next()
    yield

def process_victory():
  global Fiber, MovementFiber
  MovementFiber = None
  G.FlagMissionAbort = False
  yield from next_until_ok()
  G.GrindLevelCount -= 1
  print("Combat ends, times left:", G.GrindLevelCount)
  G.FlagPlayerTurn = True
  G.FlagRepairNeeded = True
  G.RepairOKTimestamp = 9223372036854775807
  if not G.FlagGrindEvent:
    G.FlagSwapTeamNeeded = True

def process_movements():
  global CurrentTurn
  if G.FlagGrindEvent:
    yield from action.process_instructed_movement(G.GrindLevel, CurrentTurn)
  else:
    yield from action.move_troop(G.GrindLevel, CurrentTurn)
  end_turn()

def end_turn():
  global CurrentTurn
  CurrentTurn += 1
  action.end_turn()
  G.FlagPlayerTurn = False

def start_player_turn():
  print("Player turn start, next in 4 seconds")
  G.FlagPlayerTurn = True
  uwait(4)

def update():
  global MovementFiber, FlagInit, Fiber, FlagStartEngaging
  if G.FlagMissionAbort:
    return abort_mission()

  if Fiber:
    if util.resume(Fiber):
      print("Resume grind normal fiber")
    else:
      Fiber = None
      print("Grind normal fiber finished")

  update_combat_actions()  

  if MovementFiber and stage.is_stage_combat_map():
    FlagStartEngaging = False
    print("Resume movement fiber")
    if not util.resume(MovementFiber):
      print("Movement fiber finished")
      MovementFiber = None
    return

  if stage.is_stage_victory():
    Fiber = process_victory()
  elif stage.is_stage_player_turn():
    start_player_turn()
  elif not is_battle_ready() or not G.FlagPlayerTurn:
    if not G.FlagPlayerTurn and stage.detect_player_turn():
      start_player_turn()
    return
  elif stage.is_stage_combat_map():
    if FlagInit:
      print("Battle start, times left:", G.GrindLevelCount)
      G.normal_update()
      G.ActionFiber = process_battle_start()
      FlagInit = False
      return
    else:
      MovementFiber = process_movements()
  else:
    action.random_click(*const.BattleNextPos)

def update_combat_actions():
  global Fiber, MovementFiber, FlagStartEngaging, EngagingMovementFlags, EngagingStartTime
  if stage.is_stage_engaging():
    if not FlagStartEngaging:
      FlagStartEngaging = True
      EngagingStartTime = util.get_current_time_sec()
      EngagingMovementFlags = []
    else:
      update_engaging_movements()
  elif stage.is_stage_loading():
    return
  elif stage.is_stage_victory():
    Fiber = process_victory()
  elif stage.is_stage_neutralized() or stage.is_stage_combat_event():
    Fiber = next_until_ok()
    FlagStartEngaging = False

def get_engaging_movements():
  try:
    return const.TeamEngagingMovement[G.GrindLevel][G.CurrentTeamID]
  except Exception:
    return []

def update_engaging_movements():
  global EngagingMovementFlags, EngagingStartTime
  movements = get_engaging_movements()
  for i, move in enumerate(movements):
    if util.get_current_time_sec() < EngagingStartTime + move[0]:
      continue
    if i in EngagingMovementFlags:
      continue
    EngagingMovementFlags.append(i)
    _from, _to = move[1]
    if _to == 0:
      action.random_click(*const.CombatFormationPos[_from], 10)
      uwait(0.3)
      action.random_click(*const.CombatFormationPos[0], 10)
      return
    else:
      xy1, xy2 = const.CombatFormationPos[_from], const.CombatFormationPos[_to]
      action.random_scroll_to(*xy1, *xy2, hold=False, haste=1)
      return

def abort_mission():
  global Fiber, MovementFiber
  G.FlagMissionAbort = False
  action.abort_mission()
  Fiber = None
  MovementFiber = None
  G.GrindLevelCount -= 1
  print("Mission aborted, times left:", G.GrindLevelCount)

  G.FlagPlayerTurn = True
  G.FlagRepairNeeded = True
  G.RepairOKTimestamp = 9223372036854775807
  if not G.FlagGrindEvent:
    G.FlagSwapTeamNeeded = True

  uwait(2)