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
  startrail_threshold = 300
  startring_threshold = 500
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
