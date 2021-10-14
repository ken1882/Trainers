from _G import *
from copy import deepcopy

__UCharacterCache = {}

def get_profile():
  res  = get_request('https://mist-train-east4.azurewebsites.net/api/Users/Me')['r']
  res2 = get_request('https://mist-train-east4.azurewebsites.net/api/Users/MyPreferences')['r']
  ret = {**res, **res2}
  return ret

def get_characters():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/UCharacters')
  return res['r']

def get_character_by_uid(uid):
  if uid in __UCharacterCache:
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

def format_readable_parties(data):
  ret = []
  for party in data:
    dat = deepcopy(party)
    dat['Formation'] = next((format for format in FormationDatabase if format["Id"] == party['MFormationId']), None),
    for i,ch in enumerate(party['UCharacterSlots']):
      if not ch or not ch['UCharacter']:
        continue
      mchid = ch['UCharacter']['MCharacterId']
      dat['UCharacterSlots'][i]['MCharacter'] = next((ch for ch in CharacterDatabase if ch['Id'] == mchid), None)
    ret.append(dat)

  return ret