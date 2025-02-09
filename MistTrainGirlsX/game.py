# coding: UTF-8

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
from html import unescape
from urllib.parse import unquote,urlparse,urlencode
from ast import literal_eval
from time import strptime
from bs4 import BeautifulSoup as BS
import msgpack
import pprint
import pytz

GAME_POST_HEADERS = {
  'Accept': 'application/vnd.msgpack',
  'Accept-Encoding': 'gzip, deflate, br',
  'Content-Type': 'application/vnd.msgpack',
}

NetworkExcpetionRescues = (
  ConnectTimeout, ReadTimeout, ConnectionError, ConnectionAbortedError,
  ConnectionResetError, TimeoutError, ProtocolError
)

TemporaryNetworkErrors = (
  'Object reference not set',
  'may have been modified or deleted since entities were loaded',
  'transient failure'
)

ServerList = (
  'https://mist-production-api-001.mist-train-girls.com',
  'https://app-misttrain-prod-001.azurewebsites.net',
  'https://app-misttrain-prod-002.azurewebsites.net',
  'https://mist-train-east5.azurewebsites.net',
  'https://mist-train-east4.azurewebsites.net',
  'https://mist-train-east6.azurewebsites.net',
  'https://mist-train-east7.azurewebsites.net',
  'https://mist-train-east8.azurewebsites.net',
  'https://mist-train-east9.azurewebsites.net',
  'https://mist-train-east1.azurewebsites.net',
  'https://mist-train-east2.azurewebsites.net',
  'https://mist-train-east3.azurewebsites.net',
)

STATIC_DATA_HOST = 'https://assets4.mist-train-girls.com/production-client-web-static'

ServerLocation = ''

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
SceneDatabase     = {}
PotionExpiration  = {}

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
    path = f"{STATIC_FILE_DIRECTORY}/useragent"
    if os.path.exists(path):
      with open(path, 'r') as fp:
        Session.headers['User-Agent'] = fp.read()
  log_info("User agent:", Session.headers['User-Agent'] )
  if not args.auto_reauth and not Session.headers['Authorization']:
    raise RuntimeError("Game token is required to start game without reauthorize")
  determine_server()
  load_database(True)

def determine_server():
  global Session,ServerList,ServerLocation
  for uri in ServerList:
    try:
      log_info("Trying to connect to server", uri)
      res = requests.post(f"{uri}/api/Login")
      if res.status_code == 401:
        ServerLocation = uri
        log_info("Server location set to", uri)
        return ServerLocation
      log_info("Failed with", res, res.content)
    except Exception as res:
      log_error(res)
  log_warning("Unable to get a live server")
  return _G.ERRNO_MAINTENANCE

def check_login():
  global Session,ServerLocation
  log_info("Trying to connect to server:", ServerLocation)
  url = f"{ServerLocation}/api/Login"
  res = Session.post(url=url, headers=GAME_POST_HEADERS, timeout=NetworkPostTimeout)
  if type(res) == dict or res.status_code == 401:
    log_warning("Failed login into game:", res, res.content)
    return _G.ERRNO_FAILED
  elif res.status_code == 200:
    return res
  return _G.ERRNO_MAINTENANCE

def is_response_ok(res):
  log_debug(res)
  if res.status_code != 200:
    _G.LastErrorCode = res.status_code
    if res.content:
      try:
        _G.LastErrorMessage = res.content.decode(errors='ignore')
      except Exception:
        pass
    if res.status_code == 403:
      log_error("Server is under maintenance!")
    if res.status_code == 408:
      log_error("Token expired")
    else:
      log_error(f"An error occurred during sending request to {res.url}:\n{res}\n{res.content}\n\n")
    return False
  log_debug(res.content)
  log_debug('\n')
  return True

def is_day_changing():
  curt = localt2jpt(datetime.now())
  return (curt.hour == 4 and curt.minute >= 59) or (curt.hour == 5 and curt.minute <= 1)

def change_token(token):
  global Session, GAME_POST_HEADERS
  GAME_POST_HEADERS['Authorization'] = token
  Session.headers['Authorization'] = token

def unpack(content):
  unpacker = msgpack.Unpacker()
  unpacker.feed(content)
  return list(unpacker)[1]

def get_request(url, depth=1):
  global Session,ServerLocation
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
    if not is_day_changing():
      log_warning("Server day changed")
      if FlagAutoReauth:
        reauth_game()
      break
  if not url.startswith('http'):
    url = ServerLocation + url
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
    if FlagAutoReauth and (errno == 401 or errno == 408):
      log_info("Attempting to reauth game")
      reauth_game()
      return get_request(url)
    elif errno == 500:
      return None
    else:
      # exit()
      return None
  if not res.content:
    return None
  return unpack(res.content)

def post_request(url, data=None, depth=1):
  global Session,TemporaryNetworkErrors,ServerLocation
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
    if not is_day_changing():
      log_warning("Server day changed")
      if FlagAutoReauth:
        reauth_game()
      break
  res = None
  if not url.startswith('http'):
    url = ServerLocation + url
  try:
    log_debug(f"[POST] {url} with payload:", data, sep='\n')
    if data != None:
      res = Session.post(url, data, headers=GAME_POST_HEADERS, timeout=NetworkPostTimeout)
    else:
      res = Session.post(url, headers=GAME_POST_HEADERS, timeout=NetworkPostTimeout)
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
    elif FlagAutoReauth and (errno == 401 or errno == 408):
      log_info("Attempting to reauth game")
      reauth_game()
      wait(1)
      return post_request(url, data, depth=depth)
    elif errno == 500:
      return None
    else:
      # exit()
      return None
  if not res.content:
    return None
  return unpack(res.content)

def login_dmm():
  global Session,ServerLocation
  _G.SetCacheString('DMM_MTG_COOKIES', '')
  _G.SetCacheString('DMM_FORM_DATA', '')
  Session = requests.Session()
  res  = Session.get('https://accounts.dmm.co.jp/service/login/password')
  page = BS(res.content, 'html.parser')
  form = {
    'token': page.find('input', {'name': 'token'})['value'],
    'path':   '',
    'prompt': '',
    'device': '',
  }
  form['login_id'],form['password'] = os.getenv('DMM_CREDENTIALS').split(':')
  res2 = Session.post('https://accounts.dmm.co.jp/service/login/password/authenticate', form)
  if res2.status_code != 200:
    log_error("Failed to login DMM Account:", res2, '\n', res2.content)
    return res2
  
  if 'login/totp' in res2.url:
    page  = BS(res2.content, 'html.parser')
    token = page.find('input', {'name': 'token'})['value']
    res3 = login_totp(token)
    if res3.status_code != 200 or 'login' in res3.url:
      log_error("2FA verification failed")
      res3.status_code = 401
      return res3
  
  raw_cookies = ''
  for k in Session.cookies.keys():
    raw_cookies += f"{k}={Session.cookies[k]};"
  _G.SetCacheString('DMM_MTG_COOKIES', raw_cookies)
  return res2

def login_totp(token, pin=''):
  global Session,ServerLocation
  if not pin:
    input('Enter your authenticator pin: ')
  form = {
    'token': token,
    'totp': pin,
    'path': '',
    'device': ''
  }
  return requests.post('https://accounts.dmm.co.jp/service/login/totp/authenticate', form)

def reauth_game(depth=0):
  global Session,ServerLocation
  new_token = ''
  if depth > 3:
    log_warning("Reauth depth excessed, abort")
    return _G.ERRNO_MAINTENANCE
  
  log_info("Try login game")
  try:
    raw_cookies = _G.GetCacheString('DMM_MTG_COOKIES')
    for line in raw_cookies.split(';'):
      seg = line.strip().split('=')
      k = seg[0]
      v = '='.join(seg[1:])
      Session.cookies.set(k, v)
    
    res  = Session.get('https://pc-play.games.dmm.co.jp/play/MistTrainGirlsX/')
    page = res.content.decode('utf8')
    inf_raw = re.search(r"var gadgetInfo = {((?:.*?|\n)*?)};", page).group(0)
    inf     = {}
    for line in inf_raw.split('\n'):
      line = [l.strip() for l in line.split(':')]
      if len(line) < 2:
        continue
      inf[line[0].lower()] = literal_eval(line[1].strip()[:-1])
    
    inf['url'] = unescape(unquote(inf['url']))
    inf['st']  = unquote(inf['st'])
    tmp  = inf['url'].split('&url=')[-1].split('&st=')
    _url = [u for u in tmp if u[:4] == 'http'][0]
    urld = urlparse(_url)
    
    Session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    payload = _G.GetCacheString('DMM_FORM_DATA')
    ServerLocation = f"{urld.scheme}://{urld.hostname}"
    payload = {
      'url': f"{ServerLocation}/api/DMM/auth?fromGadget=true",
      'gadget': _url,
      'st': inf['st'],
      'httpMethod': 'POST',
      'headers': 'Content-Type=application%2Fx-www-form-urlencoded',
      'postData': 'key=value',
      'authz': 'signed',
      'contentType': 'JSON',
      'numEntries': '3',
      'getSummaries': 'false',
      'signOwner': 'true',
      'signViewer': 'true',
      'container': 'dmm',
      'bypassSpecCache': '',
      'getFullHeaders': 'false',
      'oauthState': '',
      'OAUTH_SIGNATURE_PUBLICKEY': 'key_2032',
    }
    payload = urlencode(payload)

    res = Session.post('https://osapi.dmm.com/gadgets/makeRequest', payload)
    log_debug("Response:", res)
    content = ''.join(res.content.decode('utf8').split('>')[1:])
    data = json.loads(content)
    log_debug(data)
    if "'rc': 403" in str(data):
      return _G.ERRNO_MAINTENANCE
    new_token = json.loads(data[list(data.keys())[0]]['body'])
  except Exception as err:
    log_error("Unable to reauth game:", err)
    handle_exception(err)
  finally:
    Session.headers = GAME_POST_HEADERS
  
  if new_token:
    log_info("Game connected")
    change_token(f"Bearer {new_token['r']}")
    res = check_login()
    if type(res) == int:
      return _G.ERRNO_MAINTENANCE
    res = get_request('/api/Home')
  else:
    log_warning("Failed to login to game")
    return None
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
  global FieldSkillDatabase,QuestDatabase,ABStoneDatabase,SceneDatabase,PotionExpiration
  links = [
    '/MasterData/MCharacterViewModel.json',
    '/MasterData/MEnemyViewModel.json',
    '/MasterData/MFormationViewModel.json',
    '/MasterData/MSkillViewModel.json',
    '/MasterData/MLinkSkillViewModel.json',
    '/MasterData/MItemViewModel.json',
    '/MasterData/MWeaponViewModel.json',
    '/MasterData/MArmorViewModel.json',
    '/MasterData/MAccessoryViewModel.json',
    '/MasterData/MCharacterPieceViewModel.json',
    '/MasterData/MFieldSkillViewModel.json',
    '/MasterData/MQuestViewModel.json',
    '/MasterData/MCharacterGearLevelViewModel.json',
    '/MasterData/MAbilityStoneViewModel.json',
    '/MasterData/MSceneViewModel.json',
    '/MasterData/MApRecoveryItemViewModel.json',
  ]
  for i,link in enumerate(links):
    path = f"{STATIC_FILE_DIRECTORY}/{link.split('/')[-1]}"
    db = None
    if forced or not os.path.exists(path) or time() - os.path.getmtime(path) > STATIC_FILE_TTL:
      try:
        log_info("Loading", link)
        db = requests.get(STATIC_DATA_HOST+link).json()
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
      ori_res = deepcopy(db)
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
      LinkSkillDatabase = {}
      for skill in ori_res:
        LinkSkillDatabase[skill['OriginMSkillId']] = skill
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
    elif i == 14:
      SceneDatabase = db
    elif i == 15:
      PotionExpiration = {}
      for _,potion in db.items():
        PotionExpiration[potion['MItemId']] = potion

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

def get_scene(id):
  if id not in SceneDatabase:
    load_database(True)
    if id not in SceneDatabase:
      raise RuntimeError(f"Invalid scene id: {id}")
  return SceneDatabase[id]

def get_item(item):
  if 'MItemId' in item:
    return get_consumable(item['MItemId'])
  elif 'MWeaponId' in item:
    return get_weapon(item['MWeaponId'])
  elif 'MArmorItem' in item:
    return get_armor(item['MArmorItem'])
  elif 'MAccessoryId' in item:
    return get_accessory(item['MAccessoryId'])
  elif 'MAbilityStoneId' in item:
    return get_abstone(item['MAbilityStoneId'])
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
  elif item['ItemType'] == ITYPE_ACCESSORY:
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

def is_potion_expired(mitem_id):
  global PotionExpiration
  if mitem_id not in PotionExpiration:
    return True
  edate = PotionExpiration[mitem_id]['EndDate']
  if not edate:
    return False
  edate = strptime(edate, '%Y-%m-%dT%H:%M:%S')
  edate = datetime(*edate[:6], tzinfo=pytz.timezone('Asia/Tokyo')).timestamp()
  curt = localt2jpt(datetime.now()).timestamp()
  if curt >= edate:
    return True
  return False

def get_current_events():
  pass

