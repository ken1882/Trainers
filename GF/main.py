from multiprocessing import set_start_method, freeze_support, Pool
import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time, random, sys
import G, util, action, stage, const, update, Input
import numpy as np
from G import uwait, Mode
from datetime import datetime
import json
import sysargv
import grind

# assign constants
PWD = os.path.dirname(os.path.realpath(__file__))
Hwnd = win32gui.GetForegroundWindow()
LastHwnd = None
os.environ['PATH'] += ';{}\\bin'.format(PWD)
os.environ['TESSDATA_PREFIX'] = PWD + '\\bin'

if __name__ == '__main__':
  set_start_method('spawn', force=True)
  freeze_support()
  G.Pool = Pool(2)

def start():
  global LastHwnd
  util.find_app()
  util.align_window()
  util.initialize()

  if G.AppHwnd == 0:
    print("App not found, aborting")
    return exit()

  if G.FlagAlign:
    util.align_window(0,0)
  print("Start hwnd {}, max FPS: {}".format(hex(G.AppHwnd), 1/G.FPS))
  util.change_title(const.AppTitle)
  
  while G.FlagRunning:
    uwait(G.FPS, False)
    update.main_update()
    cur_hwnd = win32gui.GetForegroundWindow()

    if cur_hwnd != G.AppHwnd and not G.FlagRebooting:
      if LastHwnd == G.AppHwnd:
        print("App unfocused auto-paused")
        LastHwnd = cur_hwnd
      elif G.FlagForceFocus and G.AppHwnd and not G.FlagPaused:
        print("Force Focus Flag is set! Switch to app")
        uwait(1.2)
        action.switch2app()
      continue
    elif LastHwnd != G.AppHwnd and not G.FlagRebooting:
      print("Switched to app, begin in 1.2 seconds")
      LastHwnd = cur_hwnd
      uwait(1.2)
    
    G.CurInternCount += 1
    G.FrameCount += 1
    if G.CurInternCount >= G.InternUpdateTime:
      G.CurInternCount = 0
      util.getAppRect()
      if not G.FlagPaused:
        update.process_update()
        Input.clean_intern()

if not os.path.isdir("tmp"):
  os.mkdir("tmp")

if __name__ == "__main__":
  # load config
  Config = {}
  with open('config.py') as file:
    exec(file.read())
  G.MaxRepair = Config['MaxRepair']
  G.WorstRepairTime = Config['WorstRepairTime']
  G.StopFastRepairItemThreshold = Config['StopFastRepairItemThreshold']
  G.RetireDollNumber = Config['RetireDollNumber']
  G.MinCombatResources = Config['MinCombatResources']
  const.EditMainGunnerIndexA = Config['MainGunnerIndexA']
  const.EditMainGunnerIndexB = Config['MainGunnerIndexB']
  const.TeamEngagingMovement = Config['TeamEngagingMovement']
  const.TeamMovementPos = Config['TeamMovementPos']
  const.EventCombatMovement = Config['EventCombatMovement']
  const.EventLevelPos = Config['EventLevelPos']
  const.TeamDeployPos = Config['TeamDeployPos']
  
  print("Config Loaded:")
  for k, v in Config.items():
    if k == 'TeamEngagingMovement':
      print("\n{}:".format(k))
      for level in v:
        print("{}:".format(level))
        for i, moves in enumerate(v[level]):
          print("  Team {}:".format(i))
          for mv in moves:
            print("    Second {} => {}".format(mv[0], mv[1]))
        print('')
    elif k in ('MainGunnerIndexB', 'MainGunnerIndexA', 'EventLevelPos', 'LevelFastRepairThreshold', 'LevelWorstRepairTime'):
      print("\n{}:".format(k))
      for level in v:
        print("  {}: {}".format(level, v[level]))
    elif k == 'TeamDeployPos':
      print("\n{}:".format(k))
      for level in v:
        print("{}:".format(level))
        for tid, pos in enumerate(v[level]):
          print("  Team {}: {}".format(tid, pos))
        print('')
    elif k == 'TeamMovementPos':
      print("\n{}:".format(k))
      for level in v:
        print("{}:".format(level))
        for turn_id, turns in enumerate(v[level]):
          print("  Turn {}:".format(turn_id))
          for team_id, moves in enumerate(turns):
            print("    Team {}:".format(team_id))
            for move in moves:
              print("      {} => {}".format(move[0], move[1]))
        print('')
    elif k == 'EventCombatMovement':
      print("\n{}:".format(k))
      for level in v:
        print("{}:".format(level))
        for turn_id, turns in enumerate(v[level]):
          print("  Turn {}:".format(turn_id))
          for _i, move in enumerate(turns):
            print("    {}, {}".format(move[0], move[1:]))
        print('')
    else:
      print(k, v)
  print('-'*15)
  sysargv.load()
  try:
    G.FastRepairThreshold = Config['LevelFastRepairThreshold'][G.GrindLevel]
    G.WorstRepairTime = Config['LevelWorstRepairTime'][G.GrindLevel]
    G.CheckRepairCount = Config['CheckRepairCount'][G.GrindLevel]
  except KeyError:
    G.FastRepairThreshold = Config['FastRepairThreshold']
    G.WorstRepairTime = Config['WorstRepairTime']
    G.CheckRepairCount = Config['CheckRepairCount']['default']
  print("Repair time threshold for {}: {}".format(G.GrindLevel, G.FastRepairThreshold))
  print("Worst repair time:", G.WorstRepairTime)
  print("Autocombat/Grind Level Resources threshold:", G.MinCombatResources)
  print("Check repair count:", G.CheckRepairCount)
  print('-'*15)

def test_func():
  util.initialize()
  util.find_app()
  util.align_window()
  util.getAppRect()
  util.getPixel()
  
def test_fiber_func():
  fiber = action.swap_team()
  while util.resume(fiber):
    G.FrameCount += 1
    Input.update()
    uwait(G.FPS)    
    if Input.is_trigger(Input.keymap.kF9, False):
      break

def tmp_test_func():
  # print(stage.is_stage_neutralized())
  print(stage.get_current_stage())
  # test_fiber_func()
  action.random_click(*const.EventPos)

if __name__ == '__main__':
  try:
    if G.FlagTest:
      test_func()
      tmp_test_func()
      if G.FlagAlign:
        util.align_window(0,0)
    elif G.Mode > 0:
      start()
    elif G.Mode != -1:
      sysargv.show_help()
  finally:
    util.terminate()