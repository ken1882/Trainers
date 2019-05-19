import const, util, action, G, stage, random
from G import uwait
from threading import Thread

CDT = 10
ClickCD = [0, 0, 0]
Ready = True

def init():
  global Ready
  Ready = True

def determine_jump():
  jp = [0,0,0]
  for i, pos in enumerate(const.StrawPathPos):
    if ClickCD[i] > 0:
      ClickCD[i] -= 1
    if not stage.is_color_ok(util.getPixel(*pos), const.StrawPathColor[i]):
      jp[i] = 1
    if ClickCD[i] == 0 and not stage.is_color_ok(util.getPixel(*pos), const.StrawPathColor[i]):
      action.random_click(*pos, G.DefaultRandRange / 2)
      # th = Thread(target=action.delayed_click(*pos, 0.1, G.DefaultRandRange / 2))
      # th.start()
      ClickCD[i] = CDT
      uwait(0.03)
  if G.FlagDebug:
    print("Jump:", jp)

def is_stage_prepare():
  return stage.is_pixel_match(const.StageStrawPixel, const.StageStrawColor)

def is_stage_game():
  return stage.is_pixel_match(const.StageStrawGamePixel, const.StageStrawGameColor)

def is_game_over():
  return stage.is_pixel_match(const.StageStrawOverPixel, const.StageStrawOverColor)

def update():
  global Ready
  if is_stage_prepare():
    Ready = True
    action.random_click(*const.StrawReadyPos)
    uwait(2)
  elif is_game_over():
    print("Game over")
    Ready = False
    action.random_click(*const.StrawOverOKPos)
    G.FlagRunning = (False or G.FlagRepeat)
    uwait(3)
    return False
  elif Ready and is_stage_game():
    determine_jump()
  return True