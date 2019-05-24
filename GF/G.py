import random, time

# Global access header file

# Constants
PWD = ""
AppName = "BlueStacks"

# Program flags
FlagRunning = True
FlagPaused  = False
FlagVerbose = False
FlagTest  = False
FlagAlign = False
FlagDebug = False
FlagAutoCombat = False
FlagManualControl = False
FlagCounter = False


AutoCombatCount = -1

def Flags(name=None):
  flags = {
    'running': FlagRunning,
    'paused': FlagPaused,
    'verbose': FlagVerbose,
    'test': FlagTest,
    'autocombat': FlagAutoCombat,
    'manualcontrol': FlagManualControl,
    'counter': FlagCounter,
  }
  if name:
    name = name.lower()
    return flags[name]
  return flags


# Hwnd of this program
Hwnd    = 0

# Hwnd of target window
AppHwnd = 0

FPS = (1 / 120)
InternUpdateTime = 120
CurInternCount   = InternUpdateTime
FrameCount       = 0
FreezeTime       = 300

Mode = 0
Difficulty = 0
Counter = 0

# Not a actually const, window rect
AppRect = [0, 0, 0, 0]

# Random range for clicking to bypass detection
DefaultRandRange = 12

# generator that store current action
ActionFiber = None

# App screen image
ScreenImageFile = "tmp/app.png"

ScreenTimeout = 1000

Pool = None

def is_mode_backup():
  return Mode == 1

def is_mode_like():
  return Mode == 2

def wait(sec):
  time.sleep(sec)

def uwait(sec, rand=True):
  if rand:
    sec += random.random()
    if sec > 0.5:
      sec -= (random.random() / 3)
  wait(sec)

def setup():
  global InternUpdateTime, ScreenTimeout
  if is_mode_backup():
    InternUpdateTime = 300
  elif is_mode_like():
    InternUpdateTime = 60