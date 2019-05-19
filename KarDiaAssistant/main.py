import PIL.ImageGrab
import win32api, win32con, win32gui
import os, time, random, sys
import G, util, action, stage, freeze, const, update, Input
import numpy as np
from G import uwait, Mode
from datetime import datetime
import sysargv, slime, straw

# assign constants
PWD = os.path.dirname(os.path.realpath(__file__))
Hwnd = win32gui.GetForegroundWindow()
LastHwnd = None
os.environ['PATH'] += ';{}\\bin'.format(PWD)
os.environ['TESSDATA_PREFIX'] = PWD + '\\bin'

def start():
  global LastHwnd
  util.find_app()
  util.align_window()
  util.initialize()
  inter_timer = G.InternUpdateTime
  if G.FlagAlign:
    util.align_window(0,0)
  print("Start hwnd {}, max FPS: {}".format(hex(G.AppHwnd), 1/G.FPS))
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
    
    inter_timer += 1
    if inter_timer >= G.InternUpdateTime:
      inter_timer = 0
      util.getAppRect()
      if not G.FlagPaused:
        update.process_update()
        Input.clean_intern()

sysargv.load()

def test_func():
  util.find_app()
  util.align_window()
  util.getAppRect()
  util.getPixel()

try:
  if G.FlagTest:
    test_func()
    if G.FlagAlign:
      util.align_window(0,0)
    if G.Mode == 1:
      slime.identify(False)
      print("Gameover:", slime.is_gameover())
      print("Score:", slime.get_score())
      util.save_screenshot("tmp/slime_score.png",)
    elif G.Mode == 2:
      print(straw.is_stage_prepare())
  elif G.Mode > 0:
    start()
  else:
    sysargv.show_help()
finally:
  util.terminate()