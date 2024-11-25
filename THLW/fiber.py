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
  event_pos = ((691, 119),(688, 217),(685, 317),(685, 415))
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
  Input.rclick(*event_pos[_G.ARGV.jndex])
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
  global StageDepth,LastStage
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
  end_rematch_timestamp = datetime.now()
  battle_duration = int(_G.ARGV.battle_duration)
  for _ in range(int(_G.ARGV.index)):
    _ = next(party_sel_cycle)
  if not target_name:
    raise RuntimeError("No stage name given")
  while True:
    yield
    stg = stage.get_current_stage()
    if stg:
      if stg == LastStage:
        StageDepth += 1
      else:
        StageDepth = 0
      LastStage = stg
    if StageDepth > 100:
      _G.log_info(f"Stage {stg} too deep, close game")
      StageDepth = 0
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
      flag_fighting = False
      flag_rebooting = True
      continue
    elif stage.is_stage('Crashed'):
      close_game()
      wait(3)
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
          yield from start_stage_selection_fiber()
        except Exception:
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
      depth = 0
      while not stage.is_stage('RematchSetting'):
        depth += 1
        if depth % 5 == 0:
          Input.rclick(692, 500)
        if depth > 30:
          _G.log_info(f"Stage {stg} too deep, close game")
          StageDepth = 0
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
      if battle_duration and flag_fighting and end_rematch_timestamp < datetime.now():
        log_info("Attempt end rematch")
        Input.mouse_down(495, 86)
        StageDepth += 10
        for _ in range(10):
          wait(0.5)
          yield
        Input.mouse_up(495, 86)
        end_rematch_timestamp = datetime.now() + timedelta(seconds=30)

def start_rhythm_fiber():
  left_color = set((
    (210, 228, 254),(169, 202, 246),(187, 213, 252),(135, 181, 237),(198, 222, 250),(103, 157, 222),(140, 188, 249),
    (207, 212, 214),(113, 172, 233),(84, 119, 234),(66, 142, 244),(64, 113, 216),(118, 154, 232),(184, 239, 254),
    (34, 153, 220),(65, 255, 255),(71, 207, 245),(103, 215, 250),(124, 173, 232),(83, 153, 230),(153, 231, 255),
    (45, 206, 255),(79, 115, 223),(88, 146, 217),(41, 89, 160),(67, 135, 231),(41, 136, 185),(193, 202, 206),
    (118, 225, 253),(98, 155, 237),(41, 98, 187),(59, 196, 250),(124, 175, 244),(104, 166, 253),(57, 180, 253),
    (49, 106, 197),(87, 219, 253),(106, 217, 254),(97, 163, 228),(91, 221, 255),(127, 167, 224),(88, 102, 151),
    (76, 143, 219),(68, 132, 210),(49, 120, 154),(40, 90, 159),(91, 98, 174),(48, 99, 142),(80, 109, 163),
    (88, 94, 155),(61, 82, 183),(64, 89, 134),(56, 104, 152),(63, 123, 210),(33, 82, 164),(42, 102, 183),
    (40, 103, 183),(89, 96, 110),(48, 88, 162),
  ))
  right_color = set((
    (207, 60, 44),(247, 196, 160),(235, 70, 47),(222, 81, 23),(236, 138, 113),(243, 172, 143),(239, 103, 82),
    (253, 119, 69),(255, 251, 190),(246, 183, 148),(235, 121, 97),(235, 159, 117),(255, 128, 85),(255, 215, 164),
    (237, 151, 72),(242, 161, 135),(215, 101, 82),(220, 62, 43),(209, 83, 67),(218, 120, 85),(255, 229, 180),
    (194, 75, 67),(201, 51, 32),(229, 130, 105),(235, 148, 122),(239, 167, 138),(234, 128, 103),(255, 123, 72),
    (236, 143, 70),(182, 130, 128),(176, 170, 169),(255, 237, 184),(200, 89, 111),(240, 149, 131),(255, 154, 106),
    (247, 208, 164),(200, 65, 52),(254, 192, 152),(254, 144, 95),(239, 128, 103),(210, 55, 39),(215, 101, 82),
    (210, 55, 39),(198, 47, 34),(216, 60, 41),(210, 55, 39),(254, 144, 95),(247, 195, 153),(229, 130, 105),
    (243, 183, 138),(255, 131, 85),(203, 117, 64),(255, 209, 166),(242, 160, 127),(239, 111, 92),(234, 131, 105),
    (254, 188, 150),(255, 246, 188),(158, 70, 67),(243, 168, 139), (255, 176, 142),(243, 109, 71),(255, 121, 81),
    (253, 155, 70),(236, 154, 127),(139, 97, 87),(241, 185, 150),(254, 210, 162),(240, 155, 62),(223, 115, 95),
    (242, 165, 137),(243, 190, 145),(254, 238, 187),(248, 118, 68),(231, 112, 66),(252, 183, 142),(243, 160, 139),
    (193, 48, 36),(231, 135, 110),(238, 156, 130),(232, 140, 114),(206, 53, 38),(241, 156, 133),(156, 77, 80),
    (254, 221, 176),(242, 187, 153),(242, 182, 148),(245, 186, 152),(141, 73, 73),(255, 118, 81),(226, 134, 108),
    (244, 180, 168),(250, 198, 153),(237, 170, 121),(212, 203, 202),(247, 202, 158),(255, 129, 79),(255, 166, 127),
    (245, 176, 144),(238, 142, 116),(240, 182, 130),(230, 113, 96),(255, 158, 105),(255, 195, 153),(210, 73, 57),
    (241, 109, 88),(242, 171, 140),(203, 67, 53),(247, 198, 149),(239, 161, 131),(232, 144, 117),(240, 151, 123),
    (232, 155, 110),(246, 190, 152),(243, 131, 115),(255, 129, 74),(200, 187, 186),(254, 145, 109),(242, 105, 61),
    (253, 128, 89),(245, 139, 67),(249, 229, 177),(248, 193, 148),(253, 220, 169),(255, 209, 128),(225, 129, 100),
    (255, 125, 85),(254, 124, 75),(236, 180, 147),(255, 224, 176),(255, 211, 144),(222, 119, 96),(204, 47, 37),
    (254, 254, 185),(255, 184, 142),(244, 192, 140),(245, 178, 163),(221, 103, 83),(234, 144, 113),(255, 125, 82),
    (255, 255, 194),(236, 154, 124),
  ))
  left_color  = [pc for pc in left_color if pc[2] <= 210]
  right_color = [pc for pc in right_color if pc[0] <= 210 or pc[1] >= 100]
  while True:
    yield
    pl = graphics.get_pixel(406, 281, True)
    pr = graphics.get_pixel(570, 282, True)
    if Input.is_trigger(win32con.VK_UP):
      print('---')
    flag_beat = False
    flag_lk = (pl[2] > 210 or any((1 for pc in left_color if graphics.is_color_ok(pl, pc, 2))))
    flag_rk = ((pr[0] > 210 and pr[1] < 100) or any((True for pc in right_color if graphics.is_color_ok(pr, pc, 2))))
    if (sum(pl) > 240*3 and sum(pr) > 240*3) or (sum(pl) < 270 and sum(pr) < 270):
      continue
    if sum(pl) < 240*3 and sum(pl) > 270:
      print('L:', pl, flag_lk)
    if sum(pr) < 240*3 and sum(pr) > 270 and pr != (207, 50, 36):
      print("R:", pr, flag_rk)
    if flag_lk:
      Input.click(350, 300)
      flag_beat = True
    if flag_rk:
      Input.click(600, 300)
      flag_beat = True
    if flag_beat:
      wait(0.003)

# def start_capture_rhythm_fiber():
#   lq = []
#   rq = []
#   while True:
#     yield
#     pl = graphics.get_pixel(380, 269, True)
#     pr = graphics.get_pixel(596, 268, True)
#     if sum(pl) < 240*3 and sum(pl) > 210:
#       print(pl)
#       lq.append(pl)
#     if sum(pr) < 240*3 and sum(pr) > 210:
#       print(pr)
#       rq.append(pr)
#     if Input.is_trigger(win32con.VK_UP):
#       break
#   print([c for c in lq if sum(c) > 250])
#   print([c for c in rq if sum(c) > 250])
