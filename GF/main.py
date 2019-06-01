from multiprocessing import set_start_method, freeze_support, Pool
import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time, random, sys
import G, util, action, stage, const, update, Input
import numpy as np
from G import uwait, Mode
from datetime import datetime
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
  
  if G.FlagAlign:
    util.align_window(0,0)
  print("Start hwnd {}, max FPS: {}".format(hex(G.AppHwnd), 1/G.FPS))
  util.change_title(const.AppTitle)
  
  while G.FlagRunning:
    uwait(G.FPS, False)
    update.main_update()
    cur_hwnd = win32gui.GetForegroundWindow()

    if cur_hwnd != G.AppHwnd:
      if LastHwnd == G.AppHwnd:
        print("App unfocused auto-paused")
        LastHwnd = cur_hwnd
      continue
    elif LastHwnd != G.AppHwnd:
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
  sysargv.load()
  # load config
  Config = {}
  with open('config.py') as file:
    exec(file.read())
  G.MaxRepair = Config['MaxRepair']
  G.WorstRepairTime = Config['WorstRepairTime']
  G.FastRepairThreshold = Config['FastRepairThreshold']
  G.StopFastRepairItemThreshold = Config['StopFastRepairItemThreshold']
  const.EditMainGunnerIndexA = Config['MainGunnerIndexA']
  const.EditMainGunnerIndexB = Config['MainGunnerIndexB']
  const.TeamEngagingMovement = Config['TeamEngagingMovement']
  const.TeamMovementPos = Config['TeamMovementPos']
  print("Config Loaded:")
  for k, v in Config.items():
    print(k, v)
  print('-'*15)


def test_func():
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
  # print(stage.is_stage_engaging())
  print(stage.get_current_stage())
  # test_fiber_func()

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