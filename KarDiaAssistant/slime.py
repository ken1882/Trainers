import const, G, util, cv2, slimeai, slimegrid, copy, random
import numpy as np 
import math

GridPos = np.asarray(const.SlimeGridPos)
Grid    = slimegrid.Grid()
AI      = slimeai.AI()
EmptyGrid = [0 for i in range(16)]

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

def determine_pos(pos):
  global GridPos
  deltas = GridPos - np.asarray(pos)
  dist   = np.einsum('ij,ij->i', deltas, deltas)
  return np.argmin(dist)

def update_grid(old_grid, new_grid):
  ga = old_grid.grids(True)
  for i, v in enumerate(new_grid):
    if ga[i] == 0 and v > 0:
      ga[i] = v
  old_grid.setGridA(ga)

def identify(mov=True):
  global Grid
  util.getPixel()
  img_rgb = cv2.imread(G.ScreenImageFile)
  threshold = .87
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

  if mov:
    if _dir < 0:
      G.FlagRunning = False
      print("Game Over")
      _dir = 0
    Grid.move(_dir)
    move(_dir)
  print("moved", Grid, sep='\n')
  if G.FlagDebug:
    cv2.imwrite('result.png', img_rgb)