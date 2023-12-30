import sys,os
import pickle
from datetime import datetime
from time import sleep
from random import randint
from copy import copy, deepcopy
import traceback
import unicodedata
import pytz
from dotenv import load_dotenv
load_dotenv()

ENCODING = 'UTF-8'
IS_WIN32 = False
IS_LINUX = False

if sys.platform == 'win32':
  IS_WIN32 = True
elif sys.platform == 'linux':
  IS_LINUX = True

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

OriTerminalSettings = None
BkgTerminalSettings = None

FlagRunning = True
FlagPaused  = False
FlagWorking = False
FlagProcessingUserInput = False
FlagTrainSwap = False
FlagTrainSkill = False
FlagTrainExp   = False
FlagTrainExStatus = False

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
PersistCharacterCache = False

SIG_COMBAT_WON  = 0x1
SIG_COMBAT_LOST = 0x2
SIG_COMBAT_STOP = 0x3

STATIC_FILE_TTL = 60*60*24

CH_WIDTH = {
  'F': 2, 'H': 1, 'W': 2,
  'N': 1, 'A': 1, 'Na': 1,
}

SYMBOL_WIDTH = {
  1: '♪',
  2: '★☆【】ⅠⅡⅢ：',
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
        for cw,chars in SYMBOL_WIDTH.items():
          if ch in chars:
            w += cw
            break
        else:
          w += CH_WIDTH[sym]
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
  if d:
    ret += f"{d} day"
    ret += 's ' if d != 1 else ' '
  if ret or hr:
    ret += f"{hr} hour"
    ret += 's ' if hr != 1 else ' '
  if ret or mn:
    ret += f"{mn} minute"
    ret += 's ' if mn != 1 else ' '
  if ret or se:
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
ERROR_LOCKED        = 0x1
ERROR_LIMIT_REACHED = 0x3
ERROR_NOSTAMINA     = 0x6

ERRNO_OK          = 0x0
ERRNO_MAINTENANCE = 0x10
ERRNO_DAYCHANGING = 0x11
ERRNO_FAILED      = 0xfe
ERRNO_UNAVAILABLE = 0xff

# Battle contants
BATTLESTAT_VICTORY = 0x2

# Skill constants
SSCOPE_ENEMY = 1
SSCOPE_ALLY  = 2
STYPE_SPECIAL_SKILL = 2
STYPE_NORMAL_ATTACK = 5
STYPE_CHARGE_SKILL  = 6

SKILL_POWER = [
  '-', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS', 'US'
]
SKILL_DISTANCE = [
  'none',
  'close',
  'medium',
  'long'
]
SKILL_TARGET = [
  'none',
  'enemy',
  'ally',
  'self'
]
SKILL_RANGE = [
  'none',
  'one',
  'all',
  'random',
  'row',
  'col',
]

# Msgpacked item object
MP_USER         = 0
MP_ABSTONE      = 1
MP_ACCESSORY    = 2
MP_ARMOR        = 3
MP_PARTY        = 4
MP_PARTY_GROUP  = 5
MP_PARTY_SLOT   = 6
MP_USER_PREF    = 7 
MP_MEMORY_ITEM  = 8

# Item constants
ITYPE_WEAPON      = 1
ITYPE_ARMOR       = 2
ITYPE_ACCESSORY   = 3
ITYPE_CONSUMABLE  = 4
ITYPE_ABSTONE     = 5   # ability stone
ITYPE_GOLD        = 6
ITYPE_FREEGEM     = 7
ITYPE_GEM         = 8
ITYPE_GEAR        = 10  # aka character pieces
ITYPE_GEAR2       = 11
ITYPE_ABSTONE2    = 12

ITYPE_NAMES = {
  ITYPE_WEAPON: '武器',
  ITYPE_ARMOR: '防具',
  ITYPE_ACCESSORY: '装飾',
  ITYPE_CONSUMABLE: 'アイテム',
  ITYPE_ABSTONE: '宝珠',
  ITYPE_ABSTONE2: '宝珠',
  ITYPE_GOLD: 'ゴルード',
  ITYPE_GEAR: 'ギヤ',
  ITYPE_GEAR2: 'ギヤ',
}

WTYPE_NAMES =  [
  "",
  "拳",
  "剣",
  "斧",
  "槍",
  "鞭",
  "魔具",
  "弓",
  "杖",
  "銃"
]
WTYPE_FIST    = 1
WTYPE_SWORD   = 2
WTYPE_AXE     = 3
WTYPE_SPEAR   = 4
WTYPE_WHIP    = 5
WTYPE_TAILSMAN= 6
WTYPE_BOW     = 7
WTYPE_STAFF   = 8
WTYPW_GUN     = 9

SHOP_TYPE_EVENT = 1

RARITY_A  = 2
RARITY_S  = 3
RARITY_SS = 4
RARITY_NAME = ['C','B','A','S','SS','US']

# Events
EVETYPE_RB        = 7   # Raid Boss
EVETYPE_TR        = 8   # Treasure
EVETYPE_HSR       = 9   # High speed rail
EVETYPE_ALTER     = 10
EVETYPE_LOTTERY   = 11
EVETYPE_BR        = 12  # Boss Rush
EVETYPE_INF       = 13  # Infinity
EVETYPE_JEWEL     = 15  # 狭霧の洞穴
EVETYPE_TC        = 19  # Training Camp


LastErrorCode = 0
LastErrorMessage = ''

DERPY_WAREHOUSE_HAEDER_PATH   = '.tmp/derpy_header.dat'
DERPY_WAREHOUSE_CONTENT_PATH  = '.tmp/derpy_warehouse.dat'
CLOUD_ROOT_FOLDERNAME = 'MistTrainDB'
SCENE_CLOUD_FOLDERNAME = 'Scene'
DERPY_CLOUD_FOLDERNAME = 'Derpy'
DERPY_CLOUD_ESTIMATORS = [
  'rfr_fit_order_False-feats_all.mod',
  'rfr_fit_order_True-feats_all.mod',
  'rfc_fit_order_True-feats_all.mod',
  'knn_fit_order_True-feats_all.mod',
  'rfr_fit_order_False-feats_noreport.mod',
  'rfr_fit_order_True-feats_noreport.mod',
  'rfc_fit_order_True-feats_noreport.mod',
  'knn_fit_order_True-feats_noreport.mod',
]

SCENE_METAS = {
  'main': 'main_scene.json',
  'event': 'event_scene.json',
  'character': 'character_scene.json'
}


DERPY_TACTIC_NIGE     = 1 # 逃げ
DERPY_TACTIC_SENKO    = 2 # 先行
DERPY_TACTIC_SASHI    = 3 # 差し
DERPY_TACTIC_OI       = 4 # 追い
DERPY_DIRECTION_RIGHT = 0 # 右回り 
DERPY_DIRECTION_LEFT  = 1 # 左回り
DERPY_WEATHER_SUNNY   = 0 # 晴
DERPY_WEATHER_RAIN    = 1 # 雨
DERPY_TYPE_GRASS      = 0 # 芝
DERPY_TYPE_DIRT       = 1 # ダート
DERPY_RANGE_1200      = 0
DERPY_RANGE_2400      = 1
DERPY_RANGE_3600      = 2
DERPY_UMA_REPORT      = '_・×▲○◎' # first one is reserved
DERPY_TACTIC_LIST = [
  '', '逃げ', '先行', '差し', '追い込み'
]
DERPY_STAT_TABLE = {
  'F': 1,
  'E': 2,
  'D': 3,
  'C': 4,
  'B': 6,
  'A': 8,
}
DERPY_CONDITION_LIST = [
  '_________', # reserved
  'ケガなどし',
  '心配ですね',
  '大丈夫でし',
  '少し元気が',
  'やる気を感',
  '調子は良さ',
  '凄い意気込',
  '絶好調のよ',  
]
DERPY_CONDITION_NAME = [
  '',
  '絕不調',
  '悪そう',
  '不調',
  '微不調',
  '微好調',
  '好調',
  '凄い'
  '絶好調',
]
DERPY_GROUND_TYPE = ['芝', 'ダート']
DERPY_WEATHER_TYPE = ['晴', '雨']
DERPY_DIRECTION_TYPE = ['右回り', '左回り']
DERPY_RANGE_LIST = ['1200m', '2400m', '3600m']
DERPY_CHARACTER_COUNTRY = [
  '',
  'セントイリス',
  'ニシキ',
  'アイゼングラート',
  'ヴェルフォレット',
  'フレイマリン'
]

def make_lparam(x, y):
  return (y << 16) | x

def get_lparam(val):
  return (val & 0xffff, val >> 16)

def get_last_error():
  global LastErrorCode,LastErrorMessage
  retc = LastErrorCode
  retm = LastErrorMessage
  LastErrorCode = 0
  LastErrorMessage = ''
  return (retc, retm)


DERPY_TRAINING_LIST = [
  {'fit_order': False, 'model': 'rfr', 'feats': 'all'},
  {'fit_order': True, 'model': 'rfr', 'feats': 'all'},
  {'fit_order': True, 'model': 'rfc', 'feats': 'all'},
  {'fit_order': True, 'model': 'knn', 'feats': 'all'},
  {'fit_order': False, 'model': 'rfr', 'feats': 'noreport'},
  {'fit_order': True, 'model': 'rfr', 'feats': 'noreport'},
  {'fit_order': True, 'model': 'rfc', 'feats': 'noreport'},
  {'fit_order': True, 'model': 'knn', 'feats': 'noreport'},
  # {'fit_order': True, 'model': 'svc', 'dim_red': ''},
  # {'fit_order': True, 'model': 'svr', 'dim_red': ''},
  # {'fit_order': False, 'model': 'svr', 'dim_red': ''},
]

def make_model_name(opts):
  opts = deepcopy(opts)
  ret = f"{opts.pop('model')}_"
  ret += str(opts).translate(str.maketrans(":,(){}'",'_-     ')).replace(' ','')
  ret += ".mod"
  return ret

def extract_derpy_features(race, character, feats='all'):
  n_uma = len(race['character'])
  if feats == 'all':
    return [
      race['raceId'],
      race['direction'],
      race['grade'],
      n_uma,
      character['range'],
      abs(race['type'] - character['forte']),
      race['weather'],
      character['weather'],
      character['tactics'],
      character['report'],
      character['condition'],
      character['speed'],
      character['stamina'],
      character['number'],
      character['waku'],
      character['mCharacterBaseId'],
      character['country']
    ]
  elif feats == 'noreport':
    return [
      race['raceId'],
      race['direction'],
      race['grade'],
      n_uma,
      character['range'],
      abs(race['type'] - character['forte']),
      race['weather'],
      character['weather'],
      character['tactics'],
      character['condition'],
      character['speed'],
      character['stamina'],
      character['number'],
      character['waku'],
      character['mCharacterBaseId'],
      character['country']
    ]
  raise RuntimeError(f"Don't know how to extract features of {feats}")

def GetCacheString(key):
  try:
    # load_dotenv()
    return os.getenv(key)
  except Exception as err:
    log_error("Error while getting cache string:", err)
    return ''

def GetCacheTimestamp(key):
  try:
    # load_dotenv()
    st = float(os.getenv(key) or 0)
    st = int(st)
    return datetime.fromtimestamp(st, tz=pytz.timezone('Asia/Tokyo'))
  except Exception as err:
    log_error("Error while getting timestamp:", err)
    return datetime.now()

def SetCacheString(key, val):
  try:
    os.system(f'dotenv set {key} "{val}"')
  except Exception as err:
    log_error("Error while caching:", err)
    return None  

def SetCacheTimestamp(key, val):
  if type(val) == datetime:
    val = val.timestamp()
  try:
    os.system(f'dotenv set {key} {int(val)}')
  except Exception as err:
    log_error("Error while caching timestamp:", err)
    return False

def GetCacheBinary(key):
  if not os.path.exists(key):
    return None
  try:
    with open(key, 'rb') as fp:
      return pickle.load(fp)
  except Exception:
    uwait(0.1)
    return GetCacheBinary(key)

def SetCacheBinary(key, val):
  try:
    with open(key, 'wb') as fp:
      return pickle.dump(val, fp)
  except Exception:
    return None