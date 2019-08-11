import cv2, slimeai, slimegrid, copy, random
import const, G, util, stage, action, Input
import numpy as np 
import math
from G import uwait

GridPos = np.asarray(const.SlimeGridPos)
Grid    = slimegrid.Grid()
AI      = slimeai.AI()
EmptyGrid = [0 for i in range(16)]
CheckScoreTime  = 10
CheckScoreTimer = CheckScoreTime
Ready = True

def init():
  global Ready, Grid, AI
  Ready = True
  Grid    = slimegrid.Grid()
  AI      = slimeai.AI()

def is_gameover():
  return stage.is_pixel_match(const.StageSlimeOverPixel, const.StageSlimeOverColor)

def move(mid):
  pos = const.SlimeScrollPos.copy()
  rrange = G.DefaultRandRange * 2
  pos[0] += random.randint(-rrange*2, rrange*2)
  pos[1] += random.randint(-rrange, rrange)
  delta = 80
  if mid == 0:
    util.scroll_down(*pos, delta, True, True)
  elif mid == 1:
    util.scroll_up(*pos, delta, True, True)
  elif mid == 2:
    util.scroll_right(*pos, delta, True, True)
  elif mid == 3:
    util.scroll_left(*pos, delta, True, True)

def dir2str(_dir):
  return "↑↓←→"[_dir]

def get_score():
  return int(util.read_app_text(*const.SlimeScorePos))

def determine_pos(pos):
  global GridPos
  offset = const.getAppOffset()
  pos = (pos[0] - offset[0], pos[1] - offset[1])
  deltas = GridPos - np.asarray(pos)
  dist   = np.einsum('ij,ij->i', deltas, deltas)
  return np.argmin(dist)

def update_grid(old_grid, new_grid):
  ga = old_grid.grids(True)
  for i, v in enumerate(new_grid):
    if ga[i] == 0 and v > 0:
      ga[i] = v
  old_grid.setGridA(ga)

def is_score_check_needed():
  global CheckScoreTime, CheckScoreTimer, Grid
  if CheckScoreTimer < CheckScoreTime:
    return False
  if 2048 not in Grid or 512 not in Grid:
    return False
  return True

def is_score_enough(score):
  global Grid
  if G.FlagRestricted and (score >= 0x2EE0 or 4096 in Grid):
    return True
  return False

def identify(mov=True):
  global Grid, CheckScoreTimer, CheckScoreTime
  util.getPixel()
  util.print_window(True)
  img_rgb = cv2.imread(G.ScreenImageFile)
  threshold = .89
  slimes = EmptyGrid.copy()
  first_scan = (sum(Grid) == 0)
  for i, img in enumerate(const.SlimeImages):
    if not first_scan and i > 1:
      break
    if G.FlagDebug:
      print(img)
    template = cv2.imread(img)
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    w, h = template.shape[:-1]
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
      if pt[1] < const.SlimeGridBoundY:
        continue      
      pos = determine_pos(pt)
      slimes[pos] = 2 ** (i+1)
      if G.FlagDebug:
        print(pt, determine_pos(pt))
      cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), const.SlimeColors[i], 2)

  
  new_grid = slimegrid.Grid()
  new_grid.setGridA(slimes)
  if G.FlagDebug:
    print(new_grid)
  update_grid(Grid, new_grid)
  
  if G.FlagDebug:
    for i, v in enumerate(Grid):
      if v == 0:
        continue
      pt = tuple(const.SlimeGridPos[i].copy())
      iv = int(math.log2(v)) - 1
      cv2.rectangle(img_rgb, pt, (pt[0] + 75, pt[1] + 75), const.SlimeColors[iv], 2)

  print("updated:", Grid, sep='\n')
  _dir = AI.getMove(Grid)
  print(_dir, dir2str(_dir))
  
  over = (_dir < 0)
  score = 0
  if G.FlagRestricted and is_score_check_needed():
    score = get_score()
    CheckScoreTimer = 0
  CheckScoreTimer += 1
  if over or is_score_enough(score):
    if over:
      _dir = 0
      util.save_screenshot("tmp/slime_score.png")
      print("Game Over")
    else:
      print("Enough score")
      action.random_click(*const.LeaveGamePos)
      uwait(1)
      action.random_click(*const.LeaveGameConfirm)
      uwait(7)
      return True

  if mov:
    Grid.move(_dir)
    move(_dir)

  print("moved", Grid, sep='\n')
  if G.FlagDebug:
    cv2.imwrite('tmp/result.png', img_rgb)

  return over

def update_keystate():
  if G.FlagManualControl and Input.is_trigger(Input.keymap.kCTRL, False):
    identify(G.FlagAutoPlay)

def update():
  global Ready
  if stage.is_stage_slime():
    init()
    action.random_click(*const.SlimeOKPos)
  else:
    over = False
    if Ready and not G.FlagManualControl:
      over = identify()
    over = is_gameover() or over
    if over:
      Ready = False
      print("Game over")
      util.save_screenshot("tmp/slime_score.png")
      uwait(1)
      action.random_click(*const.SlimeOverOKPos)
      G.FlagRunning = (False or G.FlagRepeat)
      uwait(3)
      return False
  return True
