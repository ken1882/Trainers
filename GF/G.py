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
FlagGrindLevel = False
FlagRepairNeeded = False
FlagSwapTeamNeeded = False
FlagEnhanceNeeded = False
FlagFastRepair = False
FlagPlayerTurn = True
FlagMaxDollReached = False
FlagRebooting = False

GrindLevel = ''
CurrentTeamID = 0

AutoCombatCount = -1
MaxRepair = 4
WorstRepairTime = 60 * 30 # 30 mins
LastMainGunner = 0
FastRepairThreshold = 2147483647
StopFastRepairItemThreshold = 30
RetireDollNumber = 12
LastFreezeTime = 0
FronzenStopThershold = 60 * 10

def Flags(name=None):
  flags = {
    'running': FlagRunning,
    'paused': FlagPaused,
    'verbose': FlagVerbose,
    'test': FlagTest,
    'autocombat': FlagAutoCombat,
    'manualcontrol': FlagManualControl,
    'counter': FlagCounter,
    'grindlevel': FlagGrindLevel,
    'repair': FlagRepairNeeded,
    'enhance': FlagEnhanceNeeded,
    'fast-repair': FlagFastRepair,
    'team-swap': FlagSwapTeamNeeded,
    'player-turn': FlagPlayerTurn,
    'doll-maxout': FlagMaxDollReached,
    'rebooting': FlagRebooting,
  }
  if name:
    name = name.lower()
    return flags[name]
  return flags


# Hwnd of this program
Hwnd    = 0

# Hwnd of target window
AppHwnd = 0

# Hwnd of BS Tweaker to re-launch app
BSTHwnd = 0
BSTRect = [0,0,0,0]

FPS = (1 / 120)
InternUpdateTime = 120
CurInternCount   = InternUpdateTime
FrameCount       = 0
FreezeTimeOut    = 120

CurTime = 0
Mode = 0
Difficulty = 0
Counter = 0
RepairOKTimestamp = 0

# Not a actually const, window rect
AppRect = [0, 0, 0, 0]

# Random range for clicking to bypass detection
DefaultRandRange = 20

# generator that store current action
ActionFiber = None
LaterFiber  = None

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

def uwait(sec, rand_scale = 0.3):
  if rand_scale:
    sec += random.uniform(rand_scale/2, rand_scale*1.5)
    if sec > 0.5:
      sec -= random.uniform(rand_scale/4, rand_scale)
  wait(sec)

def setup():
  global InternUpdateTime, ScreenTimeout, FlagAutoCombat, AutoCombatCount
  if FlagAutoCombat and AutoCombatCount == -1:
    print("Warning: Inf Auto-combat")
    AutoCombatCount = 2147483647

  if is_mode_backup():
    InternUpdateTime = 300
  elif is_mode_like():
    InternUpdateTime = 60

_LastInternUT = 0
_LastST = 0
def save_update_frequency():
  global _LastInternUT, _LastST, InternUpdateTime, ScreenTimeout
  _LastInternUT, _LastST = InternUpdateTime, ScreenTimeout

def restore_update_frequency():
  global _LastInternUT, _LastST, InternUpdateTime, ScreenTimeout
  if _LastInternUT == 0 or _LastST == 0:
    return
  InternUpdateTime, ScreenTimeout = _LastInternUT, _LastST
  _LastInternUT, _LastST = 0, 0

def superslow_update():
  global InternUpdateTime, ScreenTimeout
  InternUpdateTime = 300
  ScreenTimeout = 2000

def slow_update():
  global InternUpdateTime, ScreenTimeout
  InternUpdateTime = 120
  ScreenTimeout = 1000

def normal_update():
  global InternUpdateTime, ScreenTimeout
  InternUpdateTime = 60
  ScreenTimeout = 500

def fast_update():
  global InternUpdateTime, ScreenTimeout
  InternUpdateTime = 30
  ScreenTimeout = 100

def ultrafast_update():
  global InternUpdateTime, ScreenTimeout
  InternUpdateTime = 15
  ScreenTimeout = 80