from time import sleep
import win32con,win32api
import _G, utils
from _G import uwait
import Input
import stage, position, graphics

def start_refight_fiber():
  n = _G.ARGV.repeats or 0
  while n >= 0:
    sleep(1)
    yield
    if stage.is_stage('CombatVictory') or stage.is_stage('CombatRewards'):
      for _ in range(5):
        yield
        Input.rclick(500, 650)
        sleep(0.5)
    elif stage.is_stage('CombatResult'):
      Input.click(*position.CombatRefight)
      n -= 1
      _G.log_info(f"Refight, times left: {n}")
    elif stage.is_stage('NewScene'):
      Input.rclick(631, 623)
      yield
      sleep(1)
    elif stage.is_stage('EventReward'):
      Input.rclick(635, 526)
      yield
      sleep(1)
    elif stage.is_stage('KakinAd'):
      Input.rclick(1177, 73)
      yield
      sleep(1)
    elif stage.is_stage('EventBoss'):
      Input.rclick(*position.RaidBossStart)
      n -= 1
      _G.log_info(f"Refight, times left: {n}")
      for _ in range(10):
        yield
        sleep(0.5)
        Input.click(*position.StartBattle)

def start_initiate_fiber():
  lasts = []
  stack_size = 8
  diff_threshold = 30
  startrail_threshold = 420
  startring_threshold = 450
  cnt = 0
  rcnt = 0
  while True:
    yield
    rcnt += 1
    if rcnt > 300:
      utils.redetect_window()
      rcnt = 0
    if not stage.is_stage('CombatInitiate'):
      lasts = []
      continue
    _G.log_debug(cnt)
    if cnt < 1:
      cnt += 1
      continue
    else:
      cnt = 0
    while True:
      col = graphics.get_pixel(*position.RocketStartPos, True)
      _G.log_debug(col)
      if sum(col) < diff_threshold:
        continue
      ssize = len(lasts)
      if ssize < stack_size:
        lasts.insert(0, col)
        continue
      cs = 0
      for c in lasts:
        cs += sum(c)
      cs /= stack_size
      cv = sum(col)
      _G.log_debug(cs, cv)
      if cs > startrail_threshold:
        break
      if cv > startring_threshold and cv - cs > diff_threshold or _G.ARGV.auxiliary:
        print(cv, cs)
        ppos = win32api.GetCursorPos()
        Input.click(500, 300)
        win32api.SetCursorPos(ppos)
        break
      lasts.insert(0, col)
      lasts.pop()

def start_test_fiber():
  while True:
    print(graphics.get_pixel(*position.RocketStartPos, True))

def start_daily_fiber():
  pos_list = ((357, 659),(635, 408),(875, 218),(875, 218),(1069, 508),(859, 355),(793, 484),(319, 32),(246, 32),(909, 371),(919, 200),(1100, 508),(860, 354),(775, 484),(340, 39),(295, 39),(46, 34),(649, 547),(887, 220),(868, 202),(1084, 510),(862, 353),(804, 473),(302, 38),(257, 38),(877, 362),(905, 200),(1069, 514),(863, 354),(783, 478),(350, 38),(232, 38),(891, 507),(870, 221),(895, 194),(1068, 506),(847, 360),(795, 475),(310, 31),(157, 42),(152, 663),(1106, 555),(1125, 573),)
  for pos in pos_list:
    Input.click(*pos)
    yield from _G.rwait(5)

def start_exchange_fiber():
  while True:
    yield
    pos = (533, 281)
    if not graphics.is_color_ok(graphics.get_pixel(*pos, True), (252, 253, 253)):
      _G.log_info("Items are all exchanged")
      return
    Input.rclick(*pos)
    yield from _G.rwait(1)
    pos = (697, 610)
    if not graphics.is_color_ok(graphics.get_pixel(*pos, True), (242, 237, 118)):
      _G.log_info("Not enough tokens")
      return
    for _ in range(3):
      Input.rclick(853, 334)
      yield
    Input.rclick(*pos)
    while not stage.is_stage('PurchaseComplete'):
      yield
    Input.rclick(647, 23)
    yield from _G.rwait(1)