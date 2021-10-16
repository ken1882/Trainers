import requests
import sys
from datetime import datetime,timedelta
from time import sleep,gmtime,strftime
from random import randint
from copy import copy
import json
import traceback
import unicodedata
import os
from time import time

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

MsgPipeContinue = '\x00\x50\x00CONTINUE\x00'
MsgPipeStop  = "\x00\x50\x00STOP\x00"
MsgPipeError = "\x00\x50\x00ERROR\x00"
MsgPipeTerminated = "\x00\x50\x00TERMINATED\x00"
MsgPipeRet = "\x00\x50\x00RET\x00"
MsgPipeInfo = "\x00\x50\x00INFO\x00"

ThreadPool = {}

CVMatchHardRate  = 0.7    # Hard-written threshold in order to match
CVMatchStdRate   = 1.22   # Similarity standard deviation ratio above average in consider digit matched
CVMatchMinCount  = 1      # How many matched point need to pass
CVLocalDistance  = 10     # Template local maximum picking range

Throttling = False
StarbrustStream = True
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
ERROR_SUCCESS    = 0x0
ERROR_NOSTAMINA  = 0x6

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

LastErrorCode = 0

PostHeaders = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}

def is_response_ok(res):
  global LastErrorCode
  log_debug(res)
  if res.status_code != 200:
    LastErrorCode = res.status_code
    if res.status_code == 403:
      log_error("Server is under maintenance!")
    else:
      log_error(f"An error occurred during sending request:\n{res}\n{res.content}\n\n")
    return False
  log_debug(res.json())
  log_debug('\n')
  return True

def is_day_changing():
  curt = localt2jpt(datetime.now())
  return (curt.hour == 4 and curt.minute >= 58) or (curt.hour == 5 and curt.minute < 3)

def get_request(url):
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
  res = Session.get(url)
  if not is_response_ok(res):
    exit()
  if not res.content:
    return None
  return res.json()

def post_request(url, data=None):
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
  res = None
  if data:
    res = Session.post(url, json.dumps(data), headers=PostHeaders)
  else:
    res = Session.post(url)
  if not is_response_ok(res):
    exit()
  if not res.content:
    return None
  return res.json()

def jpt2localt(jp_time):
  '''
  Convert Japanese timezone (GMT+9) datetime object to local timezone
  '''
  time_jp = +9
  time_local = int(strftime("%z", gmtime())) // 100
  delta = time_jp - time_local
  return jp_time - timedelta(hours=delta)

def localt2jpt(local_time):
  time_jp = +9
  time_local = int(strftime("%z", gmtime())) // 100
  delta = time_jp - time_local
  return local_time + timedelta(hours=delta)

def make_lparam(x, y):
  return (y << 16) | x

def get_lparam(val):
  return (val & 0xffff, val >> 16)


CharacterDatabase = {}
EnemyDatabase     = {}
FormationDatabase = {}
SkillDatabase     = {}
LinkSkillDatabase = {}
ConsumableDatabase= {}
WeaponDatabase    = {}
ArmorDatabase     = {}
AccessoryDatabase = {}
GearDatabase      = {}
FieldSkillDatabase= {}
QuestDatabase     = {}

def load_database(forced=False):
  global VerboseLevel
  global CharacterDatabase,EnemyDatabase,FormationDatabase,SkillDatabase,LinkSkillDatabase
  global ConsumableDatabase,WeaponDatabase,ArmorDatabase,AccessoryDatabase,GearDatabase
  global FieldSkillDatabase,QuestDatabase
  links = [
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MCharacterViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MEnemyViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MFormationViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MSkillViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MLinkSkillViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MItemViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MWeaponViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MArmorViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MAccessoryViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MCharacterPieceViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MFieldSkillViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MQuestViewModel.json'
  ]
  for i,link in enumerate(links):
    path = f"{STATIC_FILE_DIRECTORY}/{link.split('/')[-1]}"
    db = None
    if forced or not os.path.exists(path) or time() - os.path.getmtime(path) > STATIC_FILE_TTL:
      try:
        db = get_request(link)
      except (SystemExit, Exception) as err:
        log_error(f"Error occurred ({err}) while requesting database, using local instead")
    # Init dbs
    if db:
      with open(path, 'w') as fp:
        fp.write(json.dumps(db,indent=2))
    else:
      with open(path, 'r') as fp:
        db = json.load(fp)
    try:
      _tmp = __convert2indexdb(db)
      db = _tmp
    except Exception:
      pass
    if i == 0:
      CharacterDatabase = db
    elif i == 1:
      EnemyDatabase = db
    elif i == 2:
      FormationDatabase = db
    elif i == 3:
      SkillDatabase = db
    elif i == 4:
      LinkSkillDatabase = db
    elif i == 5:
      ConsumableDatabase = db
    elif i == 6:
      WeaponDatabase = db
    elif i == 7:
      ArmorDatabase = db
    elif i == 8:
      AccessoryDatabase = db
    elif i == 9:
      GearDatabase = db
    elif i == 10:
      FieldSkillDatabase = db
    elif i == 11:
      QuestDatabase = db

def __convert2indexdb(db):
  ret = {}
  for obj in db:
    ret[obj['Id']] = obj
  return ret

def get_character_base(id):
  if id not in CharacterDatabase:
    load_database(True)
    if id not in CharacterDatabase:
      raise RuntimeError(f"Invalid character id: {id}")
  return CharacterDatabase[id]

def get_skill(id):
  if id not in SkillDatabase:
    load_database(True)
    if id not in SkillDatabase:
      raise RuntimeError(f"Invalid skill id: {id}")
  return SkillDatabase[id]

def get_enemy(id):
  if id not in EnemyDatabase:
    load_database(True)
    if id not in EnemyDatabase:
      raise RuntimeError(f"Invalid enemy id: {id}")
  return EnemyDatabase[id]

def get_consumable(id):
  if id not in ConsumableDatabase:
    load_database(True)
    if id not in ConsumableDatabase:
      raise RuntimeError(f"Invalid consunable id: {id}")
  return ConsumableDatabase[id]

def get_weapon(id):
  if id not in WeaponDatabase:
    load_database(True)
    if id not in WeaponDatabase:
      raise RuntimeError(f"Invalid weapon id: {id}")
  return WeaponDatabase[id]

def get_armor(id):
  if id not in ArmorDatabase:
    load_database(True)
    if id not in ArmorDatabase:
      raise RuntimeError(f"Invalid armor id: {id}")
  return ArmorDatabase[id]

def get_accessory(id):
  if id not in AccessoryDatabase:
    load_database(True)
    if id not in AccessoryDatabase:
      raise RuntimeError(f"Invalid accessory id: {id}")
  return AccessoryDatabase[id]

def get_gear(id):
  if id not in GearDatabase:
    load_database(True)
    if id not in GearDatabase:
      raise RuntimeError(f"Invalid gear id: {id}")
  return GearDatabase[id]

def get_formation(id):
  if id not in FormationDatabase:
    load_database(True)
    if id not in FormationDatabase:
      raise RuntimeError(f"Invalid formation id: {id}")
  return FormationDatabase[id]

def get_fskill(id):
  if id not in FieldSkillDatabase:
    load_database(True)
    if id not in FieldSkillDatabase:
      raise RuntimeError(f"Invalid field kill id: {id}")
  return FieldSkillDatabase[id]

def get_quest(id):
  if id not in QuestDatabase:
    load_database(True)
    if id not in QuestDatabase:
      raise RuntimeError(f"Invalid quest id: {id}")
  return QuestDatabase[id]

def get_item(item):
  if 'ItemType' not in item or 'ItemId' not in item:
    log_warning("Invalid item object: ", item)
    return item
  id = item['ItemId']
  if item['ItemType'] == ITYPE_CONSUMABLE:
    return get_consumable(id)
  elif item['ItemType'] == ITYPE_WEAPON:
    return get_weapon(id)
  elif item['ItemType'] == ITYPE_ARMOR:
    return get_armor(id)
  elif item['ItemType'] == ITYPE_ACCESORY:
    return get_accessory(id)
  elif item['ItemType'] == ITYPE_GEAR:
    return get_gear(id)
  else:
    log_warning(f"Unknown item type: {item['ItemType']} for {item}")
  return item

def get_item_name(item):
  item = get_item(item)
  if 'Name' in item:
    return item['Name']
  elif 'MCharacterId' in item:
    ch = get_character_base(item['MCharacterId'])
    return f"ギヤ：{ch['Name']}{ch['MCharacterBase']['Name']}"
  if 'ItemType' in item and 'ItemId' in item:
    return f"Item type {item['ItemType']} id:{item['ItemId']}"
  return str(item)

Session = requests.Session()
Session.headers = {
  'Authorization': sys.argv[1] if len(sys.argv) >= 2 else ''
}
load_database()