from datetime import datetime
from time import sleep
from random import random
from copy import copy
import sys
import json

IS_WIN32 = False
IS_LINUX = False

if sys.platform == 'win32':
  IS_WIN32 = True
elif sys.platform == 'linux':
  IS_LINUX = True

ARGV = {}

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

CVMatchHardRate  = 0.7    # Hard-written threshold in order to match
CVMatchStdRate   = 1.22   # Similarity standard deviation ratio above average in consider digit matched
CVMatchMinCount  = 1      # How many matched point need to pass
CVLocalDistance  = 10     # Template local maximum picking range

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

WaitInterval = 0.5
def wait(sec):
  sleep(sec)

def uwait(sec):
  sleep(sec + max(random() / 2, sec * random() / 5))


### Loading process
UmaNumberImage = []
for i in range(10):
  UmaNumberImage.append(f"UmaTemplate/{i}.png")
ImageSkillUp  = "UmaTemplate/up.png"
ImageSkillUp2 = "UmaTemplate/up2.png"
ImageRaceRanking = [
  'UmaTemplate/ranking_1.png',
  'UmaTemplate/ranking_2.png',
  'UmaTemplate/ranking_3.png',
  'UmaTemplate/ranking_4.png',
  'UmaTemplate/ranking_5.png',
]

UmaSkillData = {}
with open("UmaLibrary/SkillData.json", 'r', encoding='utf8') as fp:
  UmaSkillData = json.load(fp)['Skill']

UmaEventData = {}
with open("UmaLibrary/UmaMusumeLibrary.json", 'r', encoding='utf8') as fp:
  raw = json.load(fp)
  # Character
  for star in raw['Charactor']:
    for char in raw['Charactor'][star]:
      for event in raw['Charactor'][star][char]['Event']:
        name = list(event.keys())[0]
        if name in UmaEventData:
          continue
        UmaEventData[name] = event[name]
        for idx,option in enumerate(event[name]):
          if option['Effect'] == '上に同じ':
            UmaEventData[name][idx]['Effect'] = UmaEventData[name][idx-1]['Effect']
  # Support Card
  for rarity in raw['Support']:
    for card in raw['Support'][rarity]:
      for event in raw['Support'][rarity][card]['Event']:
        name = list(event.keys())[0]
        if name in UmaEventData:
          continue
        UmaEventData[name] = event[name]

with open("UmaLibrary/UmaMusumeLibraryMainStory.json", 'r', encoding='utf8') as fp:
  raw = json.load(fp)
  for chap in raw['MainStory']:
    for scenario in raw['MainStory'][chap]:
      for event in raw['MainStory'][chap][scenario]['Event']:
        name = list(event.keys())[0]
        if name in UmaEventData:
          continue
        UmaEventData[name] = event[name]

UmaRaceData = {}
with open("UmaLibrary/RaceDataLibrary.json", 'r', encoding='utf8') as fp:
  raw = json.load(fp)
  for tier in raw['Race']:
    for race in raw['Race'][tier]:
      UmaRaceData[race['Name']] = race
CommonRaces = ['ファイナルズ決勝', 'ファイナルズ準決勝', 'ファイナルズ予選', 'メイクデビュー']
### Program Depended Constants/Variables

CurrentUmaName = ''
CurrentUma     = None
CurrentDate    = 0  # before start
CurrentAction  = None
NextObjectiveIndex = 0
CurrentAttributes  = [0,0,0,0,0,0]
CurrentOwnedSkills = []
CurrentStatus      = 2
CurrentRaceData    = None
IgnoreStatLimit    = False
MinGetSkillPoints  = 200
MaxGetSkillPoints  = 300

ActionTrain     = 0
ActionRest      = 1
ActionHeal      = 2
ActionRace      = 3
ActionGetSkill  = 4
ActionPlay      = 5
ActionObjective = 6