import os
from time import sleep
import _G, fiber
from _G import (log_error,log_debug,log_info,log_warning,wait,uwait,resume)
import utils, Input, graphics
import win32con,win32gui
from threading import Thread
from datetime import datetime
import argv_parse

# Cache for pos/col records
output_cache = []

def print_cache():
  pos = ""
  col = ""
  print(output_cache)
  for i,ss in enumerate(output_cache):
    if i & 1 == 0:
      pos += ss 
    else:
      col += ss
  print('-'*42)
  print(f"({pos})")
  print('-'*42)
  print(f"({col})")

def detect_app_window():
  utils.find_app_window()
  # utils.find_child_window()
  _G.AppInputHwnd = _G.AppHwnd

def update_detector():
  last_tick = 0
  while _G.FlagRunning:
    sleep(_G.FPS*2)
    if _G.FrameCount == last_tick:
      continue
    if Input.is_trigger(win32con.VK_F5):
      print("Received redetect signal",flush=True)
      last_tick = _G.FrameCount
    elif Input.is_trigger(win32con.VK_F6):
      print("Received position signal",flush=True)
      last_tick = _G.FrameCount
    elif Input.is_trigger(win32con.VK_F7):
      print("Received pause signal",flush=True)
      last_tick = _G.FrameCount
    elif Input.is_trigger(win32con.VK_F8):
      print("Received worker signal",flush=True)
      last_tick = _G.FrameCount
    elif Input.is_trigger(win32con.VK_F9):
      print("Received termination signal",flush=True)
      last_tick = _G.FrameCount

def update_input():
  if not utils.is_focused():
    return
  Input.update()
  if Input.is_trigger(win32con.VK_F5):
    print("Redetecting app window")
    detect_app_window()
  elif Input.is_trigger(win32con.VK_F6):
    res = graphics.get_mouse_pixel()
    if not _G.SelectedFiber:
      output_cache.extend(res)
    print(Input.get_cursor_pos(), res) 
  elif Input.is_trigger(win32con.VK_F7):
    log_info("Worker unpaused" if _G.FlagPaused else "Worker paused")
    _G.FlagPaused ^= True
  elif Input.is_trigger(win32con.VK_F8):
    log_info("Worker terminated" if _G.FlagWorking else "Worker started")
    log_info(f"Frame count: {_G.FrameCount} / {_G.LastFrameCount}")
    _G.FlagWorking ^= True
    _G.Fiber = _G.SelectedFiber()
  elif Input.is_trigger(win32con.VK_F9):
    log_info("Stop program requested") 
    _G.FlagWorking = False
    _G.FlagRunning = False
    print_cache()
  
def main_loop():
  global output_cache
  _G.flush()
  update_input()
  if _G.WORKER_TTL and datetime.now() >= _G.WORKER_TTL:
    _G.log_info("Auto terminate due to WORKER_TTL")
    _G.FlagRunning = False
    exit()
  if not _G.FlagPaused and _G.Fiber and not resume(_G.Fiber):
    log_info(f"Worker ended, return value: {_G.pop_fiber_ret()}")
    _G.Fiber = None 
    _G.FlagWorking = False

def start_main():
  _th = Thread(target=update_detector)
  _th.start()
  try:
    while _G.FlagRunning:
      _G.FrameCount += 1
      main_loop()
      sleep(_G.FPS)
  finally:
    _G.FlagRunning = False

if __name__ == "__main__":
  utils.get_self_hwnd()
  detect_app_window()
  # utils.resize_app_window()
  args = argv_parse.load()
  if args.job:
    for method in dir(fiber):
      if args.job in method and 'fiber' in method:
        _G.SelectedFiber = getattr(fiber,method)
        log_info(f"Fiber set to {method}")
        break
  if _G.WORKER_TTL:
    _G.log_info("Worker TTL set:", datetime.strftime(_G.WORKER_TTL, '%Y-%m-%d %H:%M:%S'))
  try:
    start_main()
  except (KeyboardInterrupt, SystemExit):
    _G.FlagRunning = False