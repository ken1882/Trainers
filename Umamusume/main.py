import os
from time import sleep
import _G, fiber
from _G import (log_error,log_debug,log_info,log_warning,wait,uwait,resume)
import util, Input, graphics, stage
import win32con,win32gui
from threading import Thread
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

def update_input():
  Input.update()
  if Input.is_trigger(win32con.VK_F6):
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

  if not _G.FlagPaused and _G.Fiber and not resume(_G.Fiber):
    log_info(f"Worker ended, return value: {_G.pop_fiber_ret()}")
    _G.Fiber = None 
    _G.FlagWorking = False
    

def start_main():
  while _G.FlagRunning:
    _G.FrameCount += 1
    main_loop()
    sleep(_G.FPS)

if __name__ == "__main__":
  util.find_app_window()
  util.resize_app_window()
  util.move_window(x=1,y=1)
  util.move_window(x=-9,y=-31)
  args = argv_parse.load()
  if args.job:
    for method in dir(fiber):
      if args.job in method:
        _G.SelectedFiber = getattr(fiber,method)
        print(f"Fiber set to {method}")
        break
  try:
    start_main()
  except (KeyboardInterrupt, SystemExit):
    pass