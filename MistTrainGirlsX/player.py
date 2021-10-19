from _G import *
import game
from copy import deepcopy

__UCharacterCache = {}

MIST_GEAR_ID = 85

def clear_cache():
  global __UCharacterCache
  __UCharacterCache = {}
  
def get_profile():
  res  = game.get_request('https://mist-train-east4.azurewebsites.net/api/Users/Me')['r']
  res2 = game.get_request('https://mist-train-east4.azurewebsites.net/api/Users/MyPreferences')['r']
  ret = {**res, **res2}
  return ret

def get_characters():
  res = game.get_request('https://mist-train-east4.azurewebsites.net/api/UCharacters')
  return res['r']

def __cache_characters(chars):
  global __UCharacterCache
  for ch in chars:
    __UCharacterCache[ch['Id']] = ch

def get_character_by_uid(uid, flush=False):
  if not flush and uid in __UCharacterCache:
    return __UCharacterCache[uid]
  __cache_characters(get_characters())
  return __UCharacterCache[uid]

def get_current_parties():
  upid = get_profile()['UPartyId']
  res = game.get_request(f"https://mist-train-east4.azurewebsites.net/api/UParties/GetUPartiesFromUPartyId/{upid}")
  return res['r']

def interpret_parties(data):
  ret = []
  for party in data:
    dat = deepcopy(party)
    dat['Formation'] = game.get_formation(party['MFormationId']),
    if type(dat['Formation']) == tuple:
      dat['Formation'] = dat['Formation'][0]
    for i,ch in enumerate(party['UCharacterSlots']):
      if not ch or not ch['UCharacter']:
        continue
      mchid = ch['UCharacter']['MCharacterId']
      dat['UCharacterSlots'][i]['MCharacter'] = game.get_character_base(mchid)
    ret.append(dat)

  return ret

def log_party_status():
  if VerboseLevel < 3:
    return
  NAME_WIDTH  = 50
  POWER_WIDTH = 8
  HP_WIDTH    = 7
  string  = '\n' + '='*30 + ' Parties ' + '='*30 + '\n'
  pdat = get_current_parties()
  ppd  = interpret_parties(pdat['UParties'])
  for party in ppd:
    string += f"Party#{party['PartyNo']} Id:{party['Id']} (Name: {party['Name'] or ''})\n"
    string += f"Formation: {party['Formation']['Name']}\n"
    string += format_padded_utfstring(('名前', NAME_WIDTH), ('戦力', POWER_WIDTH, True), ('HP', HP_WIDTH, True)) + '\n'
    for ch in party['UCharacterSlots']:
      if not ch['UCharacterId']:
        continue
      string += format_padded_utfstring(
        (f"{ch['MCharacter']['Name']}{ch['MCharacter']['MCharacterBase']['Name']}", NAME_WIDTH),
        (ch['TotalStatus'], POWER_WIDTH, True),
        (ch['UCharacter']['UCharacterBaseViewModel']['Status']['HP'], HP_WIDTH, True),
      ) + '\n'
    string += '-'*69+'\n'
  log_info(string)

def get_aprecovery_items():
  res = game.get_request('https://mist-train-east4.azurewebsites.net/api/UItems/ApRecoveryItems')
  return res['r']

def use_aprecovery_item(item, amount=1):
  if amount > item['Stock']:
    log_warning(f"Not enough items in stock for use: {item}")
    return None
  return game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Users/recoverStamina/{item['MItemId']}/{amount}")  

def get_consumable_stock(id):
  items = game.get_request('https://mist-train-east4.azurewebsites.net/api/UItems')
  if items:
    items = items['r']
  return next((it for it in items if it['MItemId'] == id), None)

def get_gear_stock(id):
  items = game.get_request('https://mist-train-east4.azurewebsites.net/api/UCharacterPieces')
  if items:
    items = items['r']
  return next((it for it in items if it['MCharacterPieceId'] == id), None)

def get_mistgear_stock():
  return get_consumable_stock(MIST_GEAR_ID)

def get_item_stock(item):
  ret = None
  kit = 'ItemType'
  kid = 'ItemId'
  if item[kit] == ITYPE_GOLD:
    ret = deepcopy(item)
    ret['Stock'] = get_profile()['Money']
  elif item[kit] == ITYPE_GEAR:
    ret = get_gear_stock(item[kid])
    ret[kit] = ITYPE_GEAR
  elif item[kit] == ITYPE_CONSUMABLE:
    ret = get_consumable_stock(item[kid])
    ret[kit] = ITYPE_CONSUMABLE
  return ret

def sell_consumable(item, amount):
  uid = item['Id']
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/UItems/{uid}/sell/{amount}")
  return res['r']

def sell_gear(item, amount):
  uid = item['UCharacterPieceId']
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/UCharacterPieces/{uid}/trade/{amount}")
  return res['r']['Items']

def sell_item(item, amount=1):
  if item['ItemType'] == ITYPE_GEAR:
    return sell_gear(item, amount)
  elif item['ItemType'] == ITYPE_CONSUMABLE:
    gain = sell_consumable(item, amount)
    return [{'ItemType': ITYPE_GOLD, 'ItemId': 0, 'ItemQuantity': gain, 'Stock': gain}]