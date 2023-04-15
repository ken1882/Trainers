import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from utils import ocr_rect
from datetime import datetime, timedelta
import action

def wait_until_stage(stg, handler=None, max_depth=10):
  depth = 0
  while not stage.is_stage(stg):
    wait(1)
    yield
    if not max_depth:
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

def start_gathering_fiber():
  while True:
    dispatched = 99
    while dispatched >= _G.ARGV.max_troop_count:
      yield from wait_until_stage('Map', max_depth=0)
      dispatched = stage.get_dispatched_troop_count()
      _G.log_info("Troops dispatched:", dispatched)
      if dispatched < _G.ARGV.max_troop_count:
        break
      for _ in range(10):
        wait(1)
        yield
    _G.log_info("Start gathering")
    Input.click(*position.MapSearchPos)
    wait(2)
    yield
    Input.click(*position.MapSearchStart)
    wait(2)
    yield
    depth = 0
    while not stage.is_map_search_found():
      wait(1)
      yield
      depth += 1
      if depth > 10:
        _G.log_warning("No resources node found, waiting for 1 minte")
        for _ in range(60):
          wait(1)
          yield
        Input.click(*position.MapSearchStart)
        wait(1)
        yield
        depth = 0
    wait(1)
    yield
    Input.click(*position.StartGatherPos)
    wait(3)
    yield from action.remove_hero(2, 3)
    Input.click(*position.DeployTroops)
