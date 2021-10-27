import re

from urllib3.exceptions import ProtocolError
import _G
from _G import *
import argv_parse
import utils
from utils import localt2jpt
from datetime import datetime
import json
import os,sys
from time import time
import requests
from requests.exceptions import *
from urllib.parse import quote_plus
import pprint

PostHeaders = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}

NetworkExcpetionRescues = (
  ConnectTimeout, ReadTimeout, ConnectionError, ConnectionAbortedError,
  ConnectionResetError, TimeoutError, ProtocolError
)

TemporaryNetworkErrors = (
  'Object reference not set',
  'Data may have been modified or deleted since entities were loaded'
)

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
ABStoneDatabase   = {}

__MAX_PROGRESSION_LEVEL = 50
GearProgressionTable = {}

Session = None

FlagAutoReauth  = False
NetworkMaxRetry = 5
NetworkGetTimeout = 5
NetworkPostTimeout = 60

def init():
  global Session,FlagAutoReauth,StarbrustStream
  args = argv_parse.load()
  log_info("Flags:", args, sep='\n')
  _G.SelfHwnd = utils.get_self_hwnd()
  Session = requests.Session()
  change_token(next((arg.strip() for arg in sys.argv if arg.strip().startswith('Bearer')), ''))
  FlagAutoReauth = True if args.auto_reauth else False
  _G.StarbrustStream = True if args.star_brust_stream else False
  _G.PersistCharacterCache = False if args.no_persist_cache else True
  if args.user_agent:
    Session.headers['User-Agent'] = args.user_agent
  else:
    path = f"{DCTmpFolder}/useragent"
    if os.path.exists(path):
      with open(path, 'r') as fp:
        Session.headers['User-Agent'] = fp.read()
  log_info("User agent:", Session.headers['User-Agent'] )
  if not args.auto_reauth and not Session.headers['Authorization']:
    raise RuntimeError("Game token is required to start game without reauthorize")
  load_database()

def is_response_ok(res):
  log_debug(res)
  if res.status_code != 200:
    _G.LastErrorCode = res.status_code
    if res.content:
      try:
        _G.LastErrorMessage = res.json()['r']['m']
      except Exception:
        pass
    if res.status_code == 403:
      log_error("Server is under maintenance!")
    else:
      log_error(f"An error occurred during sending request to {res.url}:\n{res}\n{res.content}\n\n")
    return False
  log_debug(res.content)
  log_debug('\n')
  return True

def is_day_changing():
  curt = localt2jpt(datetime.now())
  return (curt.hour == 4 and curt.minute >= 58) or (curt.hour == 5 and curt.minute < 10)

def change_token(token):
  global Session
  Session.headers['Authorization'] = token

def get_request(url, depth=1):
  global Session
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
    if not is_day_changing():
      log_info("Server day changed, attempting to reauth game")
      reauth_game()
      break
  try:
    log_debug(f"[GET] {url}")
    res = Session.get(url, timeout=NetworkGetTimeout)
  except NetworkExcpetionRescues as err:
    Session.close()
    if depth < NetworkMaxRetry:
      log_warning(f"Connection errored for {url}, retry after 3 seconds...(depth={depth+1})")
      wait(3)
      return get_request(url, depth=depth+1)
    else:
      raise err
  if not is_response_ok(res):
    errno,errmsg = get_last_error()
    if FlagAutoReauth and errno == 401:
      log_info("Attempting to reauth game")
      reauth_game()
      return get_request(url)
    else:
      exit()
  if not res.content:
    return None
  return res.json()

def post_request(url, data=None, depth=1):
  global Session,TemporaryNetworkErrors
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
    if not is_day_changing():
      log_info("Server day changed, attempting to reauth game")
      reauth_game()
      wait(1)
      break
  res = None
  try:
    log_debug(f"[POST] {url} with payload:", data, sep='\n')
    if data:
      res = Session.post(url, json.dumps(data), headers=PostHeaders, timeout=NetworkPostTimeout)
    else:
      res = Session.post(url, timeout=NetworkPostTimeout)
  except NetworkExcpetionRescues as err:
    Session.close()
    if depth < NetworkMaxRetry:
      log_warning(f"Connection errored for {url}, retry after 3 seconds...(depth={depth+1})")
      wait(3)
      return post_request(url, data, depth=depth+1)
    else:
      raise err
  if not is_response_ok(res):
    errno,errmsg = get_last_error()
    if errno == 500 and any((msg in errmsg for msg in TemporaryNetworkErrors)):
      log_warning("Temprorary server error occurred, waiting for 3 seconds")
      wait(3)
      log_warning(f"Retry connect to {url} (depth={depth+1})")
      return post_request(url, data, depth=depth+1)
    elif FlagAutoReauth and errno == 401:
      log_info("Attempting to reauth game")
      reauth_game()
      wait(1)
      return post_request(url, data, depth=depth)
    else:
      exit()
  if not res.content:
    return None
  return res.json()

def reauth_game():
  global Session
  _session = requests.Session()
  _session.headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
  }
  cookie_path = f"{DCTmpFolder}/dmmcookies.key"
  form_path   = f"{DCTmpFolder}/dmmform.key"
  if not os.path.exists(form_path) or not os.path.exists(cookie_path):
    log_error("Missing re-auth file info, abort program")
    exit()
  
  with open(cookie_path, 'r') as fp:
    raw_cookies = fp.read()

  with open(form_path, 'r') as fp:
    raw_form = fp.read()

  # Update token
  for line in raw_cookies.split('\n')[0].split(';'):
    seg = line.strip().split('=')
    k = seg[0]
    v = '='.join(seg[1:])
    _session.cookies.set(k, v)

  log_info("Updating token")
  res = _session.post('https://pc-play.games.dmm.co.jp/play/MistTrainGirlsX/check/ajax-index/', raw_form.split('\n')[0])
  if not is_response_ok(res):
    log_error("Unable to reauth game, abort")
    exit()
  
  # Replace old token with new one
  token = res.json()['result']
  log_debug("New token:", token)
  payload = raw_form.split('\n')[1]
  rep = re.search(r"st=(.+?)&", payload).group(0)
  rep = rep.split('=')[1][:-1]
  payload = payload.replace(rep, quote_plus(token))

  log_debug("Request payload:", payload, sep='\n')
  # Start game
  res = _session.post('https://osapi.dmm.com/gadgets/makeRequest', payload)
  if not is_response_ok(res):
    log_error("Unable to reauth game, abort")
    exit()
  
  content = ''.join(res.content.decode('utf8').split('>')[1:])
  data = json.loads(content)
  res_json = json.loads(data[list(data.keys())[0]]['body'])
  change_token(f"Bearer {res_json['r']}")
  wait(1)
  log_info(f"New token retrieved:\n{Session.headers['Authorization']}")
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Login')
  return res

def load_gearprogression_table(data):
  global GearProgressionTable
  for _,dat in data.items():
    rarity = dat['CharacterRarity']
    if rarity not in GearProgressionTable:
      GearProgressionTable[rarity] = [0 for _ in range(__MAX_PROGRESSION_LEVEL+1)]
    GearProgressionTable[rarity][dat['Level']] = dat['TotalExperience']

def load_database(forced=False):
  global VerboseLevel
  global CharacterDatabase,EnemyDatabase,FormationDatabase,SkillDatabase,LinkSkillDatabase
  global ConsumableDatabase,WeaponDatabase,ArmorDatabase,AccessoryDatabase,GearDatabase
  global FieldSkillDatabase,QuestDatabase,ABStoneDatabase
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
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MQuestViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MCharacterGearLevelViewModel.json',
    'https://assets.mist-train-girls.com/production-client-web-static/MasterData/MAbilityStoneViewModel.json'
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
    elif i == 12:
      load_gearprogression_table(db)
    elif i == 13:
      ABStoneDatabase = db

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

def get_character_name(id):
  ch = get_character_base(id)
  return f"{ch['Name']}{ch['MCharacterBase']['Name']}"

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

def get_abstone(id):
  if id not in ABStoneDatabase:
    load_database(True)
    if id not in ABStoneDatabase:
      raise RuntimeError(f"Invalid ability stone id: {id}")
  return ABStoneDatabase[id]

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
  elif item['ItemType'] in [ITYPE_ABSTONE, ITYPE_ABSTONE2]:
    return get_abstone(id)
  elif item['ItemType'] in [ITYPE_GEAR, ITYPE_GEAR2]:
    return get_gear(id)
  elif item['ItemType'] == ITYPE_GOLD:
    item['Name'] = 'ゴルト'
    return item
  elif item['ItemType'] == ITYPE_FREEGEM:
    item['Name'] = 'ミストジュエル (無償)'
  elif item['ItemType'] == ITYPE_GEM:
    item['Name'] = 'ミストジュエル (有償)'
  else:
    log_warning(f"Unknown item type: {item['ItemType']} for {item}")
  return item

def get_item_name(item, desc=False):
  '''
  If `desc=True`, item's description will followed by a `^` in return value
  '''
  item = get_item(item)
  if 'Name' in item:
    ret = item['Name']
    if desc and 'Description' in item:
      ret += '^' + item['Description']
    return ret
  elif 'MCharacterId' in item:
    ch = get_character_base(item['MCharacterId'])
    return f"ギヤ：{ch['Name']}{ch['MCharacterBase']['Name']}"
  if 'ItemType' in item and 'ItemId' in item:
    return f"Item type {item['ItemType']} id:{item['ItemId']}"
  return str(item)