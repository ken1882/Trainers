from _G import *
from copy import deepcopy

__UCharacterCache = {}

def clear_cache():
  global __UCharacterCache
  __UCharacterCache = {}
  
def get_profile():
  res  = get_request('https://mist-train-east4.azurewebsites.net/api/Users/Me')['r']
  res2 = get_request('https://mist-train-east4.azurewebsites.net/api/Users/MyPreferences')['r']
  ret = {**res, **res2}
  return ret

def get_characters():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/UCharacters')
  return res['r']

def get_character_by_uid(uid, flush=False):
  if not flush and uid in __UCharacterCache:
    return __UCharacterCache[uid]
  chars = get_characters()
  ret = next((ch for ch in chars if ch['Id'] == uid), None)
  if ret:
    __UCharacterCache[uid] = ret
  return ret

def get_current_parties():
  upid = get_profile()['UPartyId']
  res = get_request(f"https://mist-train-east4.azurewebsites.net/api/UParties/GetUPartiesFromUPartyId/{upid}")
  return res['r']

def interpret_parties(data):
  ret = []
  for party in data:
    dat = deepcopy(party)
    dat['Formation'] = get_formation(party['MFormationId']),
    if type(dat['Formation']) == tuple:
      dat['Formation'] = dat['Formation'][0]
    for i,ch in enumerate(party['UCharacterSlots']):
      if not ch or not ch['UCharacter']:
        continue
      mchid = ch['UCharacter']['MCharacterId']
      dat['UCharacterSlots'][i]['MCharacter'] = get_character_base(mchid)
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


def get_gear_stock(id):
  items = get_request('https://mist-train-east4.azurewebsites.net/api/UCharacterPieces')
  if items:
    items = items['r']
  return next((it for it in items if it['MCharacterPieceId'] == id), None)

def get_stock_item(item):
  if item['ItemType'] == ITYPE_GEAR:
    return get_gear_stock(item['ItemId'])
  return None

def sell_gear(item, amount):
  uid = item['UCharacterPieceId']
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/UCharacterPieces/{uid}/trade/{amount}")
  return res['r']

def sell_item(item, amount=1):
  if item['ItemType'] == ITYPE_GEAR:
    return sell_gear(item, amount)