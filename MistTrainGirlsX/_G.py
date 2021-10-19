import sys
from datetime import datetime
from time import sleep
from random import randint
from copy import copy
import traceback
import unicodedata

ARGV = {}

AppWindowName = "ミストトレインガールズ〜霧の世界の車窓から〜 X - FANZA GAMES - Google Chrome"
AppChildWindowName = "Chrome Legacy Window"
AppHwnd = 0
AppRect = [0,0,0,0]
AppPid  = 0
AppTid  = 0 
AppChildHwnd = 0

AppTargetHwnd   = 0
AppTargetUseMsg = True

SelfHwnd = 0
SelfPid  = 0

DCTmpFolder = ".tmp"
DCSnapshotFile = "snapshot.png"
STATIC_FILE_DIRECTORY = './static'

WindowWidth  = 1920
WindowHeight = 1080
WinTitleBarSize = (1, 31)
WinDesktopBorderOffset = (8,0)

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

# 0:NONE 1:ERROR 2:WARNING 3:INFO 4:DEBUG
VerboseLevel = 3
VerboseLevel = 4 if ('-v' in sys.argv or '--verbose' in sys.argv) else VerboseLevel

FlagRunning = True
FlagPaused  = False
FlagWorking = False

MSG_PIPE_CONT   = '\x00\x50\x00CONTINUE\x00'
MSG_PIPE_STOP   = "\x00\x50\x00STOP\x00"
MSG_PIPE_ERROR  = "\x00\x50\x00ERROR\x00"
MSG_PIPE_TERM   = "\x00\x50\x00TERMINATED\x00"
MSG_PIPE_RET    = "\x00\x50\x00RET\x00"
MSG_PIPE_INFO   = "\x00\x50\x00INFO\x00"

ThreadPool = {}

CVMatchHardRate  = 0.7    # Hard-written threshold in order to match
CVMatchStdRate   = 1.22   # Similarity standard deviation ratio above average in consider digit matched
CVMatchMinCount  = 1      # How many matched point need to pass
CVLocalDistance  = 10     # Template local maximum picking range

Throttling = True
StarbrustStream = False
PersistCharacterCache = True

SIG_COMBAT_WON  = 0x1
SIG_COMBAT_LOST = 0x2
SIG_COMBAT_STOP = 0x3

STATIC_FILE_TTL = 60*60*24

CH_WIDTH = {
  'F': 2, 'H': 1, 'W': 2,
  'N': 1, 'A': 1, 'Na': 1,
}

SYMBOL_WIDTH = {
  '♪': 1,
  '★': 2,
  '☆': 2,
}

def format_padded_utfstring(*tuples):
  '''
  Padding string with various charcter width, tuple format:\n
  `(text, width, pad_right=False)`\n
  If `pad_right` is set to True, the given text will right-aligned instead left\n
  '''
  global SYMBOL_WIDTH, CH_WIDTH
  ret = ''
  for dat in tuples:
    pad_right = False
    if len(dat) == 2:
      text,width = dat
    elif len(dat) == 3:
      text,width,pad_right = dat
    else:
      raise RuntimeError(f"Wrong number of arugments, expected 2 or 3 but get {len(dat)}")
    text = str(text)
    w = 0
    for ch in text:
      sym = unicodedata.east_asian_width(ch)
      if sym == 'A':
        w += SYMBOL_WIDTH[ch] if ch in SYMBOL_WIDTH else CH_WIDTH[sym]
      else:
        w += CH_WIDTH[sym]
    if width <= w:
      ret += text
    else:
      ret += (' ' * (width - w))+text if pad_right else text+(' ' * (width - w))
  return ret

def format_timedelta(dt):
  ret = ''
  d  = dt.days
  hr = dt.seconds // 3600
  mn = (dt.seconds % 3600) // 60
  se = dt.seconds % 60
  ms = dt.microseconds // 1000 
  ret += f"{d} day"
  ret += 's ' if d != 1 else ' '
  ret += f"{hr} hour"
  ret += 's ' if hr != 1 else ' '
  ret += f"{mn} minute"
  ret += 's ' if mn != 1 else ' '
  ret += f"{se} second"
  ret += 's ' if se != 1 else ' '
  ret += f"{ms}ms"
  return ret

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
    if ret and ret[0] == MSG_PIPE_RET:
      log_info("Fiber signaled return")
      FiberRet = ret[1]
      return False
  except StopIteration:
    log_info("Fiber has stopped")
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
  if StarbrustStream:
    return
  dt = randint(0,8) / 10
  dt = dt if Throttling else dt / 3
  sleep(sec+dt)

def handle_exception(err):
  err_info = traceback.format_exc()
  msg = f"{err}\n{err_info}\n"
  log_error(msg)

# Errnos
ERROR_SUCCESS       = 0x0
ERROR_LIMIT_REACHED = 0x3
ERROR_NOSTAMINA     = 0x6

# Battle contants
BATTLESTAT_VICTORY = 0x2

# Skill constants
SSCOPE_ENEMY = 1
SSCOPE_ALLY  = 2
STYPE_NORMAL_ATTACK = 5

# Item constants
ITYPE_WEAPON      = 1
ITYPE_ARMOR       = 2
ITYPE_ACCESORY    = 3
ITYPE_CONSUMABLE  = 4
ITYPE_GOLD        = 6
ITYPE_GEAR        = 10

SHOP_TYPE_EVENT = 1

RARITY_A  = 2
RARITY_S  = 3
RARITY_SS = 4

LastErrorCode = 0

def make_lparam(x, y):
  return (y << 16) | x

def get_lparam(val):
  return (val & 0xffff, val >> 16)
