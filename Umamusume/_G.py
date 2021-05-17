from datetime import datetime
from time import sleep
import random

AppWindowName = "umamusume"
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

FPS   = (1.0 / 120)
Fiber = None
DesktopDC = None
SelectedFiber = None 

ColorBiasRange = 15
CurrentStage   = None
FrameCount     = 0
LastFrameCount = -1
PosRandomRange = (8,8)

# 0:NONE 1:ERROR 2:WARNING 3:INFO 4:DEBUG
VerboseLevel = 3

FlagRunning = True
FlagPaused  = False
FlagWorking = False

MsgPipeContinue = '\x00\x50\x00CONTINUE\x00'
MsgPipeStop  = "\x00\x50\x00STO\x00P"
MsgPipeError = "\x00\x50\x00ERROR\x00"
MsgPipeTerminated = "\x00\x50\x00TERMINATED\x00"
MsgPipeRet = "\x00\x50\x00RET\x00"
MsgPipeInfo = "\x00\x50\x00INFO\x00"


UmaNumberImage = []
for i in range(10):
  UmaNumberImage.append(f"UmaNumber/{i}.png")

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
  try:
    next(fiber)
  except StopIteration:
    return False
  return True

def wait(sec):
  sleep(sec)

def uwait(sec, rand_scale = 0.3):
  if rand_scale:
    sec += random.uniform(rand_scale/2, rand_scale*1.5)
    if sec > 0.5:
      sec -= random.uniform(rand_scale/4, rand_scale)
  wait(sec)