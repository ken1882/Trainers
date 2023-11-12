import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from utils import ocr_rect
from datetime import datetime, timedelta
import action

UnknownStageCounter = 0

def wait_until_stage(stg, handler=None, max_depth=10):
  depth = 0
  while not stage.is_stage(stg):
    wait(1)
    yield
    if not max_depth:
      if handler:
        yield from handler()
      continue
    depth += 1
    if depth > max_depth-2:
      if handler:
        yield from handler()
      if depth > max_depth:
        _G.log_info(f"Stage not in {stg} and no handlers, exit")
        exit()

def start_training_fiber():
  n = _G.ARGV.repeats
  n = n if n else 2147483647
  wait_interval = _G.ARGV.train_interval
  for i in range(n):
    log_info(f"Training troop #{i+1} times")
    yield from wait_until_stage('Home', action.close_all_windows)
    inf = position.TrainInfantry
    for pos, wt in zip(inf['pos'], inf['wait']):
      Input.click(*pos)
      wait(wt)
    curt = datetime.now()
    next_t = curt + timedelta(minutes=wait_interval)
    _G.log_info("Training complete, next training time:", next_t.strftime('%Y-%m-%d %H:%M:%S'))
    while datetime.now() < next_t:
      wait(1)
      yield
    yield from wait_until_stage('Home', action.close_all_windows)
    _G.log_info("Collect trained troops")
    poses = [position.TrainInfantry['pos'][0]]
    for pos in poses:
      Input.click(*pos)
      wait(1)
      yield
    wait(1)

def on_search_cancel():
  global UnknownStageCounter
  if stage.is_stage('MapSearch'):
    Input.click(*position.CancelSearch)
    wait(1)
    yield
  stg = stage.get_current_stage()
  if not stg:
    UnknownStageCounter += 1
    _G.log_info("Unknown stage detected:", UnknownStageCounter)
    if UnknownStageCounter > 30:
      _G.log_info("Close all windows")
      UnknownStageCounter = 0
      yield from action.close_all_windows()
  else:
    UnknownStageCounter = 0

def start_gathering_fiber():
  while True:
    dispatched = 99
    while dispatched >= _G.ARGV.max_troop_count:
      yield from wait_until_stage('Map', handler=on_search_cancel ,max_depth=0)
      dispatched = stage.get_dispatched_troop_count()
      _G.log_info("Troops dispatched:", dispatched)
      # double check due to potential frame loss
      if dispatched < _G.ARGV.max_troop_count:
        for _ in range(3):
          wait(1)
          yield
        dispatched = stage.get_dispatched_troop_count()
        _G.log_info("Troops dispatched check:", dispatched)
        if dispatched < _G.ARGV.max_troop_count:
          break
      for _ in range(10):
        wait(1)
        yield
    _G.log_info("Start gathering")
    gather_opt = position.GatherFormation[dispatched]
    search_level = _G.ARGV.gather_level
    search_level = search_level if search_level else gather_opt['level']
    while not stage.is_map_search_found():
      if not stage.get_current_stage():
        yield from action.close_all_windows()
        continue
      yield from stage.ensure_stage('MapSearch', handler=action.open_map_search)
      yield from action.do_map_search(max(_G.ARGV.min_gather_level, search_level))
      for _ in range(10):
        wait(0.5)
        yield
      if search_level < 0:
        _G.log_warning("No resources found nearby, will pause for 30 minutes")

      search_level -= 1
      wait(1)
      yield
    Input.click(*position.StartGatherPos)
    for _ in range(5):
      wait(1)
      yield
    yield from action.remove_hero(*gather_opt['remove_hero'])
    wait(0.5)
    
    # if dispatched+1 == _G.ARGV.max_troop_count:
    #   for pos in position.MaxoutTroopPos:
    #     Input.click(*pos)
    #     wait(0.3)
    #   wait(0.5)

    Input.click(*position.DeployTroops)
    wait(0.03)
    Input.click(*position.DeployTroops)
    wait(1)
    yield
    if stage.is_stage('ConfirmDeploy'):
      _G.log_info("Cancel duplicated deployment and wait for 60 seconds")
      Input.click(*position.CancelDeploy)
      for _ in range(60):
        wait(1)
        yield
      Input.click(*position.CommonBackPos)
    for _ in range(3):
      wait(0.5)
      yield

def start_healing_fiber():
  while True:
    if graphics.is_pixel_match([position.HelpAvailable[0]], [position.HelpAvailable[1]], True) or \
      graphics.is_pixel_match([position.HelpAvailable2[0]], [position.HelpAvailable2[1]], True):
      Input.click(*position.HelpAvailable[0])
      wait(0.8)
    yield
    if stage.is_stage('Chat'):
      Input.click(*position.CommonBackPos)
      wait(0.5)
    if graphics.is_pixel_match([position.HealAvailable[0]], [position.HealAvailable[1]], True):
      Input.click(*position.HealAvailable[0])
      wait(1)
      Input.click(*position.StartHealing)
      # yield
      # while not stage.is_stage('Home'):
      #   yield
      wait(0.8)
      Input.click(336, 695)
      wait(0.5)
      Input.click(*position.CommonBackPos)
      wait(1)
    yield