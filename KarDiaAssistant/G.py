import random, time, slimeai

# Global access header file

# Constants
PWD = ""
AppName = "BlueStacks"


# Program flags
FlagRunning = True
FlagPaused  = False
FlagManualControl = False
FlagVerbose = False
FlagTest  = False
FlagAlign = False
FlagRestricted = True
FlagRepeat = False

def Flags(name=None):
  flags = {
    'running': FlagRunning,
    'paused': FlagPaused,
    'control': FlagManualControl,
    'verbose': FlagVerbose,
    'test': FlagTest,
    'align': FlagAlign,
    'restricted': FlagRestricted,
    'repeat': FlagRepeat,
  }
  if name:
    name = name.lower()
    return flags[name]
  return flags

ModeSlime = 1

# Hwnd of this program
Hwnd    = 0

# Hwnd of target window
AppHwnd = 0

FPS = (1 / 120)
InternUpdateTime = 60


Mode = 0
Difficulty = 0

# Not a actually const, window rect
AppRect = [0, 0, 0, 0]

AppWidth  = 477
AppHeight = 917

# Debug flag
FlagDebug = False

# Random range for clicking to bypass detection
DefaultRandRange = 12

# generator that store current action
ActionFiber = None

# App screen image
ScreenImageFile = "assets/app.png"

SlimeAI = slimeai.AI()

ScreenTimeout = 500

def wait(sec):
  time.sleep(sec)

def uwait(sec, rand=True):
  if rand:
    sec += random.random()
    if sec > 0.5:
      sec -= (random.random() / 3)
  wait(sec)