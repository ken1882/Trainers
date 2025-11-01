import re
import win32con
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from datetime import datetime, timedelta
import combat
import utils
import itertools
from PIL import Image

PARTY_SEL_POS = [
  [(815, 520),(468, 453)],
  [(815, 520),(446, 274)],
  [(815, 520),(458, 144)],
  [(815, 350),(481, 445)],
  [(815, 350),(500, 289)],
  [(815, 350),(504, 125)],
  [(815, 120),(497, 147)],
  [(815, 120),(501, 311)],
  [(815, 120),(518, 476)]
]
STAGE_NAME_OFFSET = [95, 42, 382, 60]

Cnt_NoLimitedErrand = 0
NextDojoTime = datetime.now() + timedelta(hours=8)

def to_homepage():
  Input.rclick(970, 25)
  wait(0.03)
  Input.rclick(812, 37)

def close_game():
  Input.click(514, -20, True, False)
  wait(1)

def start_errand_fiber():
  global Cnt_NoLimitedErrand
  while not stage.is_stage('HomePage'):
    yield
    if stage.StageDepth > 30:
      print('stage depth:', stage.StageDepth)
      close_game()
    if stage.is_stage('BSHome'):
      return
    to_homepage()
    wait(2)
  Input.rclick(824, 350)
  while not stage.is_stage('Errand'):
    yield
    if stage.StageDepth > 30:
      close_game()
    if stage.is_stage('BSHome'):
      return
    wait(2)
  wait(3)
  Input.rclick(49, 215)
  wait(2)
  # harvest
  _G.flush()
  completed = graphics.find_object('errand_done.png', 0.9)
  log_info("Completed errands:", completed)
  while completed:
    for _ in range(3):
      Input.rclick(*completed[0])
      wait(1)
      yield
    while not stage.is_stage('Errand'):
      yield
      if stage.StageDepth > 30:
        close_game()
      if stage.is_stage('BSHome'):
        return
      wait(2)
      Input.rclick(0, 367, rrange=(1,8))
      wait(0.3)
      Input.rclick(30, 420, rrange=(1,8))
    wait(5)
    _G.flush()
    completed = graphics.find_object('errand_done.png', 0.9)
    log_info("Completed errands:", completed)
  # dispatch
  if stage.StageDepth > 30:
      close_game()
  if stage.is_stage('BSHome'):
    return
  wait(2)
  errands_doing = graphics.find_object('errand_doing.png', 0.9)
  dispatched = len(errands_doing)
  depth = 0
  while dispatched < 3:
    log_info(f"Dispatched: {dispatched} (depth={depth})")
    wait(5)
    depth += 1
    yield
    if depth > 5:
      break
    errands_doing = graphics.find_object('errand_doing.png', 0.9)
    errands = []
    tmp_errands = graphics.find_object('GC.png', 0.9) 
    tmp_errands.extend(graphics.find_object('SC.png', 0.9))
    tmp_errands.extend(graphics.find_object('wood.png', 0.9))
    for erpos in tmp_errands:
      if any((abs(erpos[1]-edpos[1]) < 20 for edpos in errands_doing+errands)):
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
        wait(2)
        yield
    wait(5)
    yield
    if stage.StageDepth > 30:
      close_game()
    if stage.is_stage('BSHome'):
      return
    _G.flush()
    errands_doing = graphics.find_object('errand_doing.png', 0.9)
    dispatched = len(errands_doing)
    _G.log_info(f"Dispatched:", dispatched)
  _G.log_info("Errands done")

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
        wait(1)
        yield
    elif stage.is_stage('HelperSelect'):
      Input.rclick(477, 351)
      wait(5)
    elif stage.is_stage('CombatPrepare'):
      wait(2)
      Input.rclick(840, 500)
      wait(5)
    elif stage.is_stage('SceneStory'):
      wait(2)
      Input.rclick(931, 45)
      wait(2)
      for _ in range(2):
        Input.rclick(609, 401)
        wait(1.5)
    elif stage.is_stage('CombatVictory') or stage.is_stage('CombatRewards'):
      Input.rclick(509, 401)
      wait(5)
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
  event_pos = ((691, 119),(688, 217),(685, 317),(685, 415),(684, 465))
  _G.log_info("Start stage selection")
  while not stage.is_stage('HomePage'):
    yield
    if stage.StageDepth > 30:
      close_game()
    if stage.is_stage('BSHome'):
      return
    to_homepage()
    wait(2)
  Input.rclick(893, 453)
  for _ in range(20):
    yield
    wait(0.5)
  if _G.ARGV.yukkuri:
    Input.rclick(900, 500)
  else:
    Input.rclick(740, 500)
  wait(3)
  if _G.ARGV.yukkuri:
    Input.rclick(*event_pos[0])
    wait(2)
  Input.click(*event_pos[_G.ARGV.jndex])
  wait(2)
  depth = 0
  while graphics.get_difficulty() != _G.ARGV.kndex:
    if stage.StageDepth > 30:
      close_game()
    if stage.is_stage('BSHome'):
      return
    depth += 1
    Input.click(330,510)
    wait(2)
    yield
    if depth > 5:
      raise RuntimeError("Unable to reach lunatic difficulty")

StageDepth = 0
LastStage  = None
def start_refight_fiber():
  global StageDepth,LastStage,NextDojoTime
  StageScrolls = (
    (942, 170),
    (942, 220),
    (942, 300),
    (942, 380),
    (942, 460),
  )
  target_name = _G.ARGV.stage
  party_sel_cycle = itertools.cycle(PARTY_SEL_POS)
  flag_check_errands = False
  flag_rebooting = False
  flag_fighting = False
  reboot_timestamp = datetime.now()
  end_rematch_timestamp = datetime.now()
  battle_duration = int(_G.ARGV.battle_duration)
  stage.reset()
  for _ in range(int(_G.ARGV.index)):
    _ = next(party_sel_cycle)
  if not target_name:
    raise RuntimeError("No stage name given")
  if _G.ARGV.train:
    yield from start_dojo_fiber()
    yield from start_shopping_fiber()
    yield from start_errand_fiber()
    yield from start_stage_selection_fiber()
  stage.reset()
  while True:
    yield
    stg = stage.get_current_stage()
    if (not flag_fighting and stage.is_stucked()) or (flag_rebooting and datetime.now() > reboot_timestamp+timedelta(minutes=10)):
      _G.log_info(f"Stage {stg} too deep ({stage.StageDepth}), close game")
      close_game()
      wait(3)
    if stage.is_stage('BSHome'):
      # Input.click(530-120,138,True,False)
      # Input.click(530,138,True,False)
      wait(3)
      apos = graphics.find_object('app.png')[0]
      for _ in range(2):
        Input.click(apos[0]+30,apos[1]-50,True,False)
        wait(0.03)
      for _ in range(10):
        wait(1)
        yield
      reboot_timestamp = datetime.now()
      flag_fighting = False
      flag_rebooting = True
      continue
    elif stage.is_stage('Crashed'):
      close_game()
      wait(3)
      reboot_timestamp = datetime.now()
      flag_rebooting = True
    elif flag_rebooting:
      if not stage.is_stage('HomePage'):
        yield
        for _ in range(2):
          Input.click(615,400)
          for _ in range(10):
            wait(1)
            yield
        to_homepage()
        continue
      wait(2)
      flag_rebooting = False
      try:
        yield from start_errand_fiber()
        if NextDojoTime < datetime.now():
          yield from start_dojo_fiber()
          yield from start_shopping_fiber()
          NextDojoTime = datetime.now() + timedelta(hours=8)
        yield from start_stage_selection_fiber()
      except Exception:
        wait(5)
        continue
      if stage.is_stage('BSHome'):
        continue
      flag_check_errands = False
      wait(2)
      yield
    elif stage.is_stage('RematchEnd'):
      Input.rclick(480, 500)
      wait(5)
    elif stage.is_stage('StageSelect'):
      flag_fighting = False
      if flag_check_errands:
        wt = _G.ARGV.wait
        log_info(f"Waiting for {wt} seconds to recover battler stamina")
        for _ in range(int(wt)):
          wait(1-_G.FPS)
          yield
        try:
          _G.log_info("Checking errands")
          yield from start_errand_fiber()
          if NextDojoTime < datetime.now():
            yield from start_dojo_fiber()
            yield from start_shopping_fiber()
            NextDojoTime = datetime.now() + timedelta(hours=8)
          yield from start_stage_selection_fiber()
        except Exception as e:
          _G.log_error("Error occurred while checking errands:", e)
          wait(5)
          continue
        if stage.is_stage('BSHome'):
          continue
        flag_check_errands = False
        wait(1.5)
        yield
      for spos in StageScrolls:
        Input.click(*spos)
        wait(0.5)
        yield
        for pos,name in get_stage_names():
          if target_name not in name:
            continue
          Input.rclick(pos[0]+150, pos[1]+50)
          for _ in range(6):
            wait(0.8)
            yield
        wait(1)
        yield
    elif stage.is_stage('HelperSelect'):
      Input.rclick(477, 201)
      wait(3)
    elif stage.is_stage('CombatPrepare'):
      wait(3)
      log_info("Selecting party")
      Input.rclick(450, 520)
      wait(5)
      pos = next(party_sel_cycle)
      Input.mouse_down(*pos[0])
      wait(1)
      Input.mouse_up(*pos[0])
      wait(1)
      Input.rclick(*pos[1])
      wait(5)
      Input.rclick(692, 500)
      while not stage.is_stage('RematchSetting'):
        if stage.StageDepth % 5 == 0:
          Input.rclick(692, 500)
        if stage.is_stucked():
          _G.log_info(f"Stage {stg} too deep ({stage.StageDepth}), close game")
          close_game()
          wait(3)
          break
        wait(1)
        yield
      wait(1)
      Input.rclick(610, 506)
      wait(3)
      log_info("Start battle")
      Input.rclick(824, 500)
      wait(3)
      if battle_duration:
        end_rematch_timestamp = datetime.now()+timedelta(seconds=battle_duration)
        log_info("Rematch will ends at", end_rematch_timestamp.strftime('%H:%M:%S'))
      flag_fighting = True
      flag_check_errands = True
    elif stage.is_stage('Disconnected'):
      Input.rclick(599, 403)
      wait(1)
    elif stage.is_stage('CombatVictory') or stage.is_stage('CombatRewards'):
      Input.rclick(509, 401)
      wait(3)
      Input.rclick(882, 514)
    else:
      if battle_duration and flag_fighting:
        if datetime.now() > end_rematch_timestamp:
          log_info("Attempt end rematch")
          Input.mouse_down(875, 85)
          for _ in range(10):
            wait(0.5)
            yield
          Input.mouse_down(875, 85)
          for _ in range(60):
            yield
            wait(0.5)
        if datetime.now() > end_rematch_timestamp + timedelta(minutes=5):
          log_info("Closing game due to rematch timeout")
          flag_fighting = False
          close_game()
          wait(3)

def start_dojo_fiber():
  global NextDojoTime
  log_info("Start dojo training")
  while not stage.is_stage('HomePage'):
    yield
    if stage.is_stucked():
      close_game()
    if stage.is_stage('BSHome'):
      return
    to_homepage()
    wait(2)
  dojo_stgs = ['SkillTrainFinished', 'DateChanged', 'Disconnected']
  while not stage.is_stage('DojoMain'):
    yield
    if stage.is_stage('HomePage'):
      Input.rclick(502, 499)
      wait(1)
      Input.rclick(816, 295)
      continue
    if stage.is_stucked():
      close_game()
    if stage.is_stage('BSHome'):
      return
    wait(2)
    if any(stage.is_stage(stg) for stg in dojo_stgs):
      break
  for _ in range(10):
    wait(0.5)
    yield
  log_info("Checking finished training")
  while any(stage.is_stage(stg) for stg in dojo_stgs):
    Input.rclick(100, 500)
    for _ in range(20):
      wait(0.5)
      yield
  TrainSlotPos = ((623, 156),(628, 343),(618, 499),)
  FirstUnitPos = (79, 172)
  UnitConfirmPos = (877, 514)
  SkillPos = ((483, 203),(488, 360),(483, 433))
  TrainableSkill = ([(541, 482)], [(255, 159, 89)])
  SkillConfirmPos = (599, 482)
  SkillBookPos = (404, 294)
  SkillBookConfirmPos = (810, 483)
  SkillBookConfirmPos2 = (601, 396)
  for slot in TrainSlotPos:
    Input.rclick(*slot)
    while True:
      yield
      wait(0.3)
      if stage.is_stage('DojoUnitSelect'):
        break
      if stage.StageDepth > 10:
        break
    if stage.StageDepth > 10:
      log_info("Dojo unit select timeout, assume slot occupied")
      continue
    if stage.is_stage('BSHome'):
      return
    wait(3)
    Input.rclick(*FirstUnitPos)
    wait(0.5)
    Input.click(*UnitConfirmPos)
    wait(2)
    for pos in SkillPos:
      Input.click(*pos)
      for _ in range(5):
        yield
        wait(0.1)
      if stage.is_stage('BSHome'):
        return
      if not graphics.is_pixel_match(*TrainableSkill):
        continue
      Input.rclick(*SkillConfirmPos)
      break
    else:
      log_info("No trainable skill found due to some error, exit job")
      cnt = 0
      while stage.is_stage('HomePage'):
        Input.rclick(15, 15)
        wait(0.3)
        yield
        to_homepage()
        cnt += 1
        if cnt > 30:
          break
        wait(1)
      return
    for _ in range(10):
      yield
      wait(0.1)
    if stage.is_stage('BSHome'):
      return
    Input.rclick(*SkillBookPos)
    wait(0.5)
    Input.rclick(*SkillBookConfirmPos)
    wait(0.5)
    Input.rclick(*SkillBookConfirmPos2)
    log_info("Start training skill")
    for _ in range(10):
      yield
      wait(0.2)
  to_homepage()
  wait(3)

def start_shopping_fiber():
  while not stage.is_stage('HomePage'):
    yield
    if stage.StageDepth > 30:
      close_game()
    if stage.is_stage('BSHome'):
      return
    to_homepage()
    wait(2)
  Input.rclick(84, 502)
  wait(5)
  Input.rclick(940, 504)
  while not stage.is_stage('Shop'):
    yield
    wait(1)
    if stage.StageDepth > 30:
      _G.log_warning("Unable to reach shop, exit")
      return
  for _ in range(20):
    pos = graphics.find_object('shop_sc.png', 0.9)
    for mx, my in pos:
      Input.rclick(mx+50, my+50)
      wait(1)
      Input.rclick(597, 475)
      for _ in range(10):
        yield
        wait(0.5)
    Input.rclick(733, 513)
    for _ in range(10):
      yield
      wait(0.3)
  while not stage.is_stage('HomePage'):
    yield
    if stage.StageDepth > 30:
      close_game()
    if stage.is_stage('BSHome'):
      return
    wait(0.5)
    to_homepage()
    wait(1)