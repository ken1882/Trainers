from multiprocessing import set_start_method, freeze_support, Pool
import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time, random, sys
import G, util, action, stage, freeze, const, update, Input
import numpy as np
from G import uwait, Mode
from datetime import datetime
import sysargv, slime, straw, mine

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
sysargv.load()

def test_func():
  util.find_app()
  util.align_window()
  util.getAppRect()
  util.getPixel()

def tmp_test_func():
  # print(util.read_app_text(*[290, 309, 349, 320], dtype='time'))
  # print(stage.any_pixel_match(const.StrawPathPosA, const.StrawPathColor[0], True))
  print(stage.get_current_stage())
  if stage.is_stage_minigames():
    update.is_minigame_token_enough()
  elif stage.is_stage_pudding():
    print(stage.is_pudding_token_enough())
  action.random_scroll_to(*const.GiftScrollPos, const_y_axis=True, haste=2)

if __name__ == '__main__':
  try:
    if G.FlagTest:
      test_func()
      tmp_test_func()
      if G.FlagAlign:
        util.align_window(0,0)
      if G.is_mode_slime():
        slime.identify(False)
        print("Gameover:", slime.is_gameover())
        print("Score:", slime.get_score())
        util.save_screenshot("tmp/slime_score.png",)
      elif G.is_mode_straw():
        print(straw.is_stage_prepare())
      elif G.is_mode_mine():
        print(stage.is_stage_mine())
    elif G.Mode > 0:
      start()
    else:
      sysargv.show_help()
  finally:
    if G.FlagCounter:
      print("Final counter:", G.Counter)
    util.terminate()