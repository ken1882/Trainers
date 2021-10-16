import _G
from _G import log_info,log_debug,log_warning,log_error,wait,uwait
from utils import localt2jpt
from datetime import datetime
import json
import os,sys
from time import time
import requests

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
Session = None

def init():
  global Session
  Session = requests.Session()
  Session.headers = {
    'Authorization': sys.argv[1] if len(sys.argv) >= 2 else ''
  }
  load_database()

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
  global Session
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
  global Session
  while is_day_changing():
    log_warning("Server day changing, wait for 1 minute")
    wait(60)
  res = None
  if data:
    res = Session.post(url, json.dumps(data), headers=_G.PostHeaders)
  else:
    res = Session.post(url)
  if not is_response_ok(res):
    exit()
  if not res.content:
    return None
  return res.json()

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
    path = f"{_G.STATIC_FILE_DIRECTORY}/{link.split('/')[-1]}"
    db = None
    if forced or not os.path.exists(path) or time() - os.path.getmtime(path) > _G.STATIC_FILE_TTL:
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
  if item['ItemType'] == _G.ITYPE_CONSUMABLE:
    return get_consumable(id)
  elif item['ItemType'] == _G.ITYPE_WEAPON:
    return get_weapon(id)
  elif item['ItemType'] == _G.ITYPE_ARMOR:
    return get_armor(id)
  elif item['ItemType'] == _G.ITYPE_ACCESORY:
    return get_accessory(id)
  elif item['ItemType'] == _G.ITYPE_GEAR:
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