from datetime import datetime
from os import get_exec_path, name
from time import sleep
from random import random
from copy import copy
import json

AppWindowName = "MapleStory"
AppHwnd = 0
AppRect = [0,0,0,0]
AppPid  = 0
AppTid  = 0 

DriverName = "RTCore64.exe"

DCTmpFolder = ".tmp"
DCSnapshotFile = "snapshot.png"

WindowWidth  = 596
WindowHeight = 1070
WinTitleBarSize = (1, 31)
WinDesktopBorderOffset = (8,0)

DataCollectDirectory = ".traindata"

FPS   = (1.0 / 120)
Fiber = None
FiberRet = None
DesktopDC = None
SelectedFiber = None 

ColorBiasRange = 10
CurrentStage   = None
FrameCount     = 0
LastFrameCount = -1
PosRandomRange = (8,8)

SnapshotCache = {}  # OCR snapshot cache for current frame

ChildProcess  = {}
ChildPipe     = {}
MainChild     = None
MainChildName = None
MainChildPipe = None
PipeIn  = None
PipeOut = None

# 0:NONE 1:ERROR 2:WARNING 3:INFO 4:DEBUG
VerboseLevel = 3

FlagRunning = True
FlagPaused  = False
FlagWorking = False

MsgPipeContinue = '\x00\x50\x00CONTINUE\x00'
MsgPipeStop  = "\x00\x50\x00STOP\x00"
MsgPipeError = "\x00\x50\x00ERROR\x00"
MsgPipeTerminated = "\x00\x50\x00TERMINATED\x00"
MsgPipeRet = "\x00\x50\x00RET\x00"
MsgPipeInfo = "\x00\x50\x00INFO\x00"
MsgPipePause = "\x00\x50\x00PAUSE\x00"

CVMatchHardRate  = 0.9    # Hard-written threshold in order to match
CVMatchStdRate   = 1.22   # Similarity standard deviation ratio above average in consider digit matched
CVMatchMinCount  = 1      # How many matched point need to pass
CVLocalDistance  = 10     # Template local maximum picking range

ConsoleArgv = None

# Use `SendInput`, scancode instead of virtual keycode
MAPLE_KEYCODE = { 
  'ESC': 0x01,
  'F1': 0x3B,
  'F2': 0x3C,
  'F3': 0x3D,
  'F4': 0x3E,
  'F5': 0x3F,
  'F6': 0x40,
  'F7': 0x41,
  'F8': 0x42,
  'F9': 0x43,
  'F10': 0x44,
  'F11': 0x85,
  'F12': 0x86,
  '`': 0x29,
  '1': 0x02,
  '2': 0x03,
  '3': 0x04,
  '4': 0x05,
  '5': 0x06,
  '6': 0x07,
  '7': 0x08,
  '8': 0x09,
  '9': 0x0A,
  '0': 0x0B,
  '-': 0x0C,
  '=': 0x66,
  'Q': 0x10,
  'W': 0x11,
  'E': 0x12,
  'R': 0x13,
  'T': 0x14,
  'Y': 0X15,
  'U': 0x16,
  'I': 0x17,
  'O': 0x18,
  'P': 0x19,
  '[': 0x1A,
  ']': 0x1B,
  '\\': 0x2B,
  'A': 0x1E,
  'S': 0x1F,
  'D': 0x20,
  'F': 0x21,
  'G': 0x22,
  'H': 0x23,
  'J': 0x24,
  'K': 0x25,
  'L': 0x26,
  ';': 0x27,
  "'": 0x28,
  'Z': 0x2C,
  'X': 0x2D,
  'C': 0x2E,
  'V': 0x2F,
  'B': 0x30,
  'N': 0x31,
  'M': 0x32,
  ',': 0x33,
  '.': 0x34,
  '/': 0x35,
  'SHIFT': 0x2A,
  # 'SHIFT': 0x83,
  'CTRL': 0x1D,
  'ALT': 0x38,
  'SPACE': 0x39,
  'INSERT': 0xAB,
  'HOME': 0x47,
  'END': 0x4F,
  'DELETE': 0x53,
  'PAGEUP': 0x49,
  'PAGEDOWN': 0x51,
}

def format_curtime():
  return datetime.strftime(datetime.now(), '%H:%M:%S')

def log_error(*args, **kwargs):
  if VerboseLevel >= 1:
    print(f"[{format_curtime()}] [ERROR]:", *args, **kwargs)

def log_warning(*args, **kwargs):
  if VerboseLevel >= 2:
    print(f"[{format_curtime()}] [WARNING]:", *args, **kwargs)

def log_info(*args, **kwargs):
  if VerboseLevel >= 3:
    print(f"[{format_curtime()}] [INFO]:", *args, **kwargs)

def log_debug(*args, **kwargs):
  if VerboseLevel >= 4:
    print(f"[{format_curtime()}] [DEBUG]:", *args, **kwargs)

def resume(fiber):
  global Fiber,FiberRet
  ret = None
  try:
    ret = next(fiber)
    if ret and ret[0] == MsgPipeRet:
      log_debug("Fiber signaled return")
      FiberRet = ret[1]
      return False
  except StopIteration:
    log_debug("Fiber has stopped")
    return False
  return True

def resume_from(fiber):
  global FiberRet
  while resume(fiber):
    yield
  return FiberRet

def pop_fiber_ret():
  global FiberRet
  ret = copy(FiberRet)
  FiberRet = None
  return ret

def flush():
  global LastFrameCount,CurrentStage,SnapshotCache
  LastFrameCount = -1
  CurrentStage   = None
  SnapshotCache  = {}

def wait(sec):
  sleep(sec)

def uwait(sec):
  sleep(sec + max(random() / 2, sec * random() / 5))

def termiante():
  global ChildPipe,ChildProcess
  for name,proc in ChildProcess.items():
    try:
      pi,po = ChildPipe[name]
      pi.close()
      po.close()
      proc.terminate()
    except Exception:
      pass