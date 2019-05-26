import const, util, action, G, stage, random, Input
import win32con
from G import uwait

CDT = 10
ClickCD = [0, 0, 0]
Ready = False
StrawPathPos = [const.StrawPathPosA, const.StrawPathPosB, const.StrawPathPosC]

def init():
  global Ready
  Ready = True

def determine_jump():
  global StrawPathPos
  jp = [0,0,0]
  for i, posar in enumerate(StrawPathPos):
    if not G.FlagManualControl and ClickCD[i] > 0:
      ClickCD[i] -= 1
    elif stage.any_pixel_match(posar, const.StrawPathColor[i], True):
      jp[i] = 1
      mx, my = posar[0].copy()
      mx -= 70
      action.random_click(mx, my, G.DefaultRandRange / 2)
      offset = const.getAppOffset()
      mx += offset[0]
      my += offset[1]
      action.delayed_click(mx, my, 0.042, G.DefaultRandRange / 2)
      ClickCD[i] = CDT

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
  if not Ready and is_stage_prepare():
    init()
    action.random_click(*const.StrawReadyPos)
    uwait(2)
  elif is_game_over():
    print("Game over")
    Ready = False
    uwait(7)
    action.random_click(*const.StrawOverOKPos)
    G.FlagRunning = (False or G.FlagRepeat)
    return False
  elif Ready:
    if not G.FlagManualControl or Input.is_trigger(win32con.VK_CONTROL):
      determine_jump()
  return True