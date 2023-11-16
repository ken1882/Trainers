import re
from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
import combat
import utils
import itertools

PARTY_SEL_POS = [
  [(815, 526),(468, 453)],
  [(815, 526),(446, 274)],
  [(815, 526),(458, 144)],
  [(815, 358),(481, 445)],
  [(815, 358),(500, 289)],
  [(815, 358),(504, 125)],
  [(815, 120),(497, 147)],
  [(815, 120),(501, 311)],
  [(815, 120),(518, 476)]
]
STAGE_NAME_OFFSET = [95, 42, 382, 60]

Cnt_NoLimitedErrand = 0

def to_homepage():
  Input.rclick(970, 25)

def start_errand_fiber():
  global Cnt_NoLimitedErrand
  while not stage.is_stage('HomePage'):
    yield
    to_homepage()
    wait(1)
  Input.rclick(824, 350)
  while not stage.is_stage('Errand'):
    yield
    wait(1)
  wait(1.5)
  Input.rclick(49, 215)
  wait(1)
  # harvest
  _G.flush()
  completed = graphics.find_object('errand_done.png', 0.95)
  log_info("Completed errands:", completed)
  while completed:
    for _ in range(3):
      Input.rclick(*completed[0])
      wait(0.5)
      yield
    while not stage.is_stage('Errand'):
      yield
      wait(1)
      Input.rclick(50, 400)
    wait(1)
    _G.flush()
    completed = graphics.find_object('errand_done.png', 0.9)
    log_info("Completed errands:", completed)
  # dispatch
  dispatched = int(utils.ocr_rect((67,517,121,542), 'errand_num.png', num_only=True)[0])
  while dispatched < 3:
    log_info("Dispatched:", dispatched)
    wait(3)
    yield
    errands_doing = graphics.find_object('errand_doing.png', 0.9)
    errands = []
    tmp_errands = graphics.find_object('GC.png', 0.9) 
    tmp_errands.extend(graphics.find_object('SC.png', 0.9))
    tmp_errands.extend(graphics.find_object('wood.png', 0.9))
    for erpos in tmp_errands:
      if any((abs(erpos[1]-edpos[1]) < 20 for edpos in errands_doing)):
        continue
      errands.append(erpos)
    log_info("Available errands:", errands)
    if Cnt_NoLimitedErrand > 3:
      pass
    if not errands:
      Cnt_NoLimitedErrand += 1
      log_info("No errands available")
      break
    for pos in errands:
      for p in (pos, (279, 417),(845, 419),(525, 134)):
        Cnt_NoLimitedErrand = 0
        Input.rclick(*p)
        wait(1)
        yield
    wait(2)
    yield
    _G.flush()
    dispatched = int(utils.ocr_rect((67,517,121,542), 'errand_num.png', num_only=True)[0])

def start_walkstage_fiber():
  while True:
    yield
    if stage.is_stage('StageSelect'):
      news = graphics.find_object('newstage.png')
      if not news:
        log_info("No new stage, abort")
        break
      new_stage = news[0]
      Input.rclick(new_stage[0]+150, new_stage[1]+50)
      for _ in range(6):
        wait(0.5)
        yield
    elif stage.is_stage('HelperSelect'):
      Input.rclick(477, 201)
      wait(2)
    elif stage.is_stage('CombatPrepare'):
      wait(1)
      Input.rclick(824, 500)
      wait(3)
    elif stage.is_stage('SceneStory'):
      wait(1)
      Input.rclick(931, 45)
      wait(1)
      for _ in range(2):
        Input.rclick(609, 401)
        wait(1)
    elif stage.is_stage('CombatVictory'):
      Input.rclick(509, 401)
      wait(2)
      Input.rclick(882, 514)

def get_stage_names():
  ret = []
  for i,pos in enumerate(graphics.find_object('stgcompleted.png')):
    rect = (
      pos[0]+STAGE_NAME_OFFSET[0],
      pos[1]+STAGE_NAME_OFFSET[1],
      pos[0]+STAGE_NAME_OFFSET[2],
      pos[1]+STAGE_NAME_OFFSET[3],
    )
    ss = utils.ocr_rect(rect, f"stgname_{i}.png", lang='eng')
    ss = re.sub(r'[^a-zA-Z0-9]', '', ss)
    ret.append((pos, ss))
  return ret

def start_stage_selection_fiber():
  event_pos = ((691, 119),(688, 217),(685, 317),(685, 415))
  while not stage.is_stage('HomePage'):
    yield
    to_homepage()
    wait(1)
  Input.rclick(893, 453)
  for _ in range(20):
    yield
    wait(0.4)
  Input.rclick(762, 518)
  wait(1.5)
  Input.rclick(*event_pos[_G.ARGV.jndex])
  wait(1)
  depth = 0
  while graphics.get_difficulty() != 2:
    depth += 1
    Input.click(330,510)
    wait(1)
    yield
    if depth > 5:
      raise RuntimeError("Unable to reach lunatic difficulty")


def start_refight_fiber():
  target_name = _G.ARGV.stage
  party_sel_cycle = itertools.cycle(PARTY_SEL_POS)
  flag_check_errands = False
  for _ in range(int(_G.ARGV.index)):
    _ = next(party_sel_cycle)
  if not target_name:
    raise RuntimeError("No stage name given")
  while True:
    yield
    if stage.is_stage('BSHome'):
      Input.click(250,185,True,False)
      for _ in range(10):
        wait(0.5)
        yield
      while not stage.is_stage('HomePage'):
        yield
        Input.click(615,400)
        wait(5)
      wait(1)
      yield from start_errand_fiber()
      yield from start_stage_selection_fiber()
      flag_check_errands = False
      wait(1)
      yield
    elif stage.is_stage('RematchEnd'):
      Input.rclick(480, 500)
      wait(2)
    elif stage.is_stage('StageSelect'):
      if flag_check_errands:
        wt = _G.ARGV.wait
        log_info(f"Waiting for {wt} seconds to recover battler stamina")
        for _ in range(int(wt)):
          wait(1-_G.FPS)
          yield
        yield from start_errand_fiber()
        yield from start_stage_selection_fiber()
        flag_check_errands = False
        wait(1)
        yield
      for pos,name in get_stage_names():
        if target_name not in name:
          continue
        Input.rclick(pos[0]+150, pos[1]+50)
        for _ in range(6):
          wait(0.5)
          yield
    elif stage.is_stage('HelperSelect'):
      Input.rclick(477, 201)
      wait(2)
    elif stage.is_stage('CombatPrepare'):
      wait(2)
      Input.rclick(324, 518)
      wait(3)
      pos = next(party_sel_cycle)
      Input.mouse_down(*pos[0])
      wait(1)
      Input.mouse_up(*pos[0])
      wait(1)
      Input.rclick(*pos[1])
      wait(5)
      Input.rclick(692, 500)
      wait(3)
      Input.rclick(610, 506)
      wait(3)
      Input.rclick(824, 500)
      wait(3)
      flag_check_errands = True