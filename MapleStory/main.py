import os,sys
from time import sleep
import _G
from _G import (log_error,log_debug,log_info,log_warning,wait,uwait,resume)
import utils, Input, graphics
import win32con,win32api
from threading import Thread
import fiber
import argv_parse
import multiprocessing
from multiprocessing import Process,Pipe

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
  Input.update()
  if Input.is_trigger(win32con.VK_F5):
    print("Redetecting app window")
    utils.find_app_window()
  elif Input.is_trigger(win32con.VK_F6):
    res = graphics.get_mouse_pixel()
    if not _G.SelectedFiber:
      output_cache.extend(res)
    print(Input.get_cursor_pos(), res) 
  elif Input.is_trigger(win32con.VK_F7):
    log_info("Worker unpaused" if _G.FlagPaused else "Worker paused")
    _G.FlagPaused ^= True
    if _G.FlagPaused:
      utils.message_child(_G.MsgPipePause)
    else:
      utils.message_child(_G.MsgPipeContinue)
  elif Input.is_trigger(win32con.VK_F8):
    log_info("Worker terminated" if _G.FlagWorking else "Worker started")
    log_info(f"Frame count: {_G.FrameCount} / {_G.LastFrameCount}")
    _G.FlagWorking ^= True
    if _G.FlagWorking:
      if _G.SelectedFiber:
        _G.SelectedFiber()
      else:
        log_info("No job assigned")
    elif _G.MainChild:
      stop_main_child()
  elif Input.is_trigger(win32con.VK_F9):
    log_info("Stop program requested") 
    _G.FlagWorking = False
    _G.FlagRunning = False
    print_cache()

def update_pipes():
  if Input.is_trigger(win32con.VK_SPACE):
    print("Msg sent")
    if _G.MainChildPipe:
      _G.MainChildPipe[0].send("Hello World!")

def main_loop():
  global output_cache
  _G.flush()
  update_input()
  update_pipes()
  if not _G.FlagPaused and _G.MainChild and not _G.MainChild.is_alive():
    log_info(f"Subprocess worker ended unexpectedly")
    stop_main_child()

def start_main():
  Input.update()
  try:
    while _G.FlagRunning:
      _G.FrameCount += 1
      main_loop()
      sleep(_G.FPS)
  finally:
    _G.FlagRunning = False

def start_childprocess():
  pass

def stop_main_child():
  print("Terminating subprocess")
  utils.message_child(_G.MsgPipeStop)
  _G.MainChild.terminate()
  if _G.MainChildPipe:
    pi,po = _G.MainChildPipe
    pi.close()
    po.close()
  _G.MainChildPipe = None
  _G.MainChild = None
  _G.MainChildName = None
  _G.FlagWorking = False
  log_info(f"Subprocess worker ended")

if __name__ == "__main__":
  utils.find_app_window()
  args = argv_parse.load()
  if args.job:
    for method in dir(fiber):
      if args.job in method:
        _G.SelectedFiber = getattr(fiber,method)
        log_info(f"Fiber set to {method}")
        break
  try:
    start_childprocess()
    start_main()
  except (KeyboardInterrupt, SystemExit):
    _G.FlagRunning = False
  finally:
    _G.termiante()