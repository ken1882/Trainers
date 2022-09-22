from tkinter.tix import Tree
import _G
from _G import *
import game
from copy import deepcopy
import json
import os

__UCharacterCache = {}
__UCharacterStats = {}
__UStatsUnchangedTimes = {}
__UnsellableItems = set()
USTAT_UNCHANGE_THRESHOLD = 10

ConsumableInventory = {}
VoteItemId = 0

MIST_GEAR_ID = 85
SWAP_GEAR_ID = [
  {
    'weapon': [
      0,
      177034637,  # エクリプスクロウ改
      177034612,  # エクリプスブレイド改
      177034629,  # エクリプスエッジ改
      177034694,  # エクリプスグレイブ改
      177034649,  # エクリプスウィップ改
      177034621,  # エクリプスオーブ改
      177034679,  # エクリプスボウ改
      177034664,  # エクリプスケーン改
      177034702,  # エクリプスファイア改
    ],
    'armor': 26147276,  # エクリプスジャケット改
    'accessory': 33128722,  # エクリプスリング改
  },
  {
    'weapon': [
      0,
      159692763,  # エクリプスクロウ
      155914420,  # エクリプスブレイド
      157535430,  # エクリプスエッジ
      157062821,  # エクリプスグレイブ
      159692821,  # エクリプスウィップ
      159692732,  # エクリプスオーブ
      159974094,  # エクリプスボウ
      159974066,  # エクリプスケーン
      159067214,  # エクリプスファイア
    ],
    'armor': 26147275,  # エクリプスプレート改
    'accessory': 33128720,  # エクリプスネック改
  },
  {'weapon': [0,0,0,0,0,0,0,0,0,0], 'armor': 26147280, 'accessory': 33128716},
  {'weapon': [0,0,0,0,0,0,0,0,0,0], 'armor': 26147275, 'accessory': 33128718},
  {'weapon': [0,0,0,0,0,0,0,0,0,0], 'armor': 26147278, 'accessory': 33128721},
]

def clear_cache():
  global __UCharacterCache
  __UCharacterCache = {}
  
def get_profile():
  res  = game.get_request('/api/Users/Me')['r']
  res2 = game.get_request('/api/Users/MyPreferences')['r']
  ret = {**res, **res2}
  return ret

def get_unfinished_combat():
  pf = get_profile()
  if not pf['InCombat']:
    return None
  return {
    'MQuestId': pf['MQuestId'],
    'UPartyId': pf['UPartyId'],
  }

def get_characters():
  res = game.get_request('/api/UCharacters')
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

def get_consumables():
  res = game.get_request('/api/UItems')
  return res['r']

def get_weapons():
  res = game.get_request('/api/UWeapons')
  return res['r']

def get_armors():
  res = game.get_request('/api/UArmors')
  return res['r']

def get_accessories():
  res = game.get_request('/api/UAccessories')
  return res['r']

def get_abstones():
  res = game.get_request('/api/UAbilityStones')
  return res['r']

def get_gears():
  res = game.get_request('/api/UCharacterPieces')
  res = res['r']
  # key = 'MCharacterId'
  # for idx,item in enumerate(res):
  #   res[idx][key] = game.get_gear(item['MCharacterPieceId'])[key]
  return res

def get_all_items(flatten=False):
  '''
  If `flatten=True`, return list instead of dict
  '''
  ret = {
    ITYPE_WEAPON: [{**{'ItemId': item['MWeaponId'], 'ItemType': ITYPE_WEAPON}, **item} for item in get_weapons()],
    ITYPE_ARMOR: [{**{'ItemId': item['MArmorId'], 'ItemType': ITYPE_ARMOR}, **item} for item in get_armors()],
    ITYPE_ACCESSORY: [{**{'ItemId': item['MAccessoryId'], 'ItemType': ITYPE_ACCESSORY}, **item} for item in get_accessories()],
    ITYPE_CONSUMABLE: [{**{'ItemId': item['MItemId'], 'ItemType': ITYPE_CONSUMABLE}, **item} for item in get_consumables()],
    ITYPE_ABSTONE: [{**{'ItemId': item['MAbilityStoneId'], 'ItemType': ITYPE_ABSTONE}, **item} for item in get_abstones()],
    ITYPE_GEAR: [{**{'ItemId': item['MCharacterPieceId'],'ItemType': ITYPE_GEAR}, **item} for item in get_gears()],
  }
  if flatten:
    ar = []
    for _,a in ret.items():
      ar += a
    return ar
  return ret

def is_character_mastered(ch, accumulate=False, check_stat=True):
  global __UCharacterStats,__UStatsUnchangedTimes
  sk_keys = ['USkill1','USkill2','USkill3']
  skills = [ch[sk] for sk in sk_keys]
  if any([sk['Rank'] < 99 for sk in skills]):
    return False
  if not check_stat:
    return True
  res = game.get_request(f"/api/UCharacters/{ch['UCharacterBaseId']}/BaseStatusUp")
  mstatus = res['r']['MaxStatuses'][-1]
  sstats = 0
  flag_maxed = True
  for k,v in ch['UCharacterBaseViewModel']['Status'].items():
    sstats += v
    if v < mstatus[k]:
      flag_maxed = False
  if accumulate:
    mid = ch['MCharacterId']
    if mid not in __UCharacterStats:
      __UCharacterStats[mid] = sstats
      __UStatsUnchangedTimes[mid] = 0
      return flag_maxed
    log_info(f"{game.get_character_name(mid)}: {sstats} {__UStatsUnchangedTimes[mid]}")
    if __UCharacterStats[mid] == sstats:
      if __UStatsUnchangedTimes[mid] > USTAT_UNCHANGE_THRESHOLD:
        return True
      __UStatsUnchangedTimes[mid] += 1
    else:
      __UCharacterStats[mid] = sstats
      __UStatsUnchangedTimes[mid] = 0
  return flag_maxed

def get_maxed_partymember(pid, sid):
  '''
  Get party stats maxed party member uid of given stage
  '''
  res = game.get_request(f"/api/Quests/{sid}/prepare/{pid}?rentalUUserId=null")
  ret = []
  for ch in res['r']['QuestPreparationCharacterViewModels']:
    if _G.FlagTrainSkill and not is_character_mastered(get_character_by_uid(ch['UCharacterId']), check_stat=False):
      continue
    if all([n == 0 for _,n in ch['GrowStatus'].items()]):
      ret.append(ch['UCharacterId'])
      continue
  return ret

def get_unmastered_characters():
  '''
  Get characters that still has unmastered skills or status
  '''
  chars = get_characters()
  ret = []
  for ch in chars:
    if not is_character_mastered(ch):
      ret.append(ch)
  return ret

def get_current_parties():
  '''
  Get 10 parties of current group
  '''
  upid = get_profile()['UPartyId']
  res = game.get_request(f"/api/UParties/GetUPartiesFromUPartyId/{upid}")
  return res['r']

def get_party_by_pid(pid):
  res = game.get_request(f"/api/Quests/208001101/prepare/{pid}?rentalUUserId=null")
  return res['r']['UPartyViewModel']

def interpret_parties(data):
  '''
  Add comprehensive data to raw party data
  '''
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

def format_character_data(characters):
  NAME_WIDTH  = 50
  RARITY_WIDTH = 7
  POWER_WIDTH = 8
  HP_WIDTH    = 7
  string = format_padded_utfstring(
    ('名前', NAME_WIDTH), ('ランク', RARITY_WIDTH, True), ('戦力', POWER_WIDTH, True), ('HP', HP_WIDTH, True),
  ) + '\n'
  for ch in characters:
    if 'UCharacterId' in ch and not ch['UCharacterId']:
      continue
    if 'MCharacter' not in ch:
      chid = ch['MCharacterId'] if 'MCharacterId' in ch else 0
      if 'UCharacter' in ch:
        chid = ch['UCharacter']['MCharacterId']
      if chid:
        ch['MCharacter'] = game.get_character_base(chid)
    if 'UCharacter' not in ch:
      ch['UCharacter'] = ch
    string += format_padded_utfstring(
      (f"{ch['MCharacter']['Name']}{ch['MCharacter']['MCharacterBase']['Name']}", NAME_WIDTH),
      (RARITY_NAME[ch['MCharacter']['CharacterRarity']], RARITY_WIDTH, True),
      (ch['TotalStatus'], POWER_WIDTH, True),
      (ch['UCharacter']['UCharacterBaseViewModel']['Status']['HP'], HP_WIDTH, True),
    ) + '\n'
  return string

def format_item_data(items):
  NAME_WIDTH  = 50
  ITYPE_WIDTH = 10
  STOCK_WIDTH = 10
  string = format_padded_utfstring(
    ('種類', ITYPE_WIDTH), ('名前', NAME_WIDTH), ('所持数', STOCK_WIDTH)
  ) + '\n'
  item_dict = {}
  for item in items:
    name = game.get_item_name(item)
    stock = item['Stock'] if 'Stock' in item else 1
    if stock <= 0:
      continue
    if name not in item_dict:
      item_dict[name] = [item['ItemType'], 0]
    item_dict[name][1] += stock
  
  for name,item in item_dict.items():
    string += format_padded_utfstring(
      (ITYPE_NAMES[item[0]], ITYPE_WIDTH),
      (name, NAME_WIDTH),
      (item[1], STOCK_WIDTH),
    ) + '\n'
  return string

def log_party_status():
  if VerboseLevel < 3:
    return
  string  = '\n' + '='*30 + ' Parties ' + '='*30 + '\n'
  pdat = get_current_parties()
  ppd  = interpret_parties(pdat['UParties'])
  for party in ppd:
    string += f"Party#{party['PartyNo']} Id:{party['Id']} (Name: {party['Name'] or ''})\n"
    string += f"Formation: {party['Formation']['Name']}\n"
    string += format_character_data(party['UCharacterSlots'])
    string += '-'*69+'\n'
  log_info(string)

def get_aprecovery_items():
  res = game.get_request('/api/UItems/ApRecoveryItems')
  return res['r']

def use_aprecovery_item(item, amount=1):
  if amount > item['Stock']:
    log_warning(f"Not enough items in stock for use: {item}")
    return None
  return game.post_request(f"/api/Users/recoverStamina/{item['MItemId']}/{amount}")  

def get_consumable_stock(id):
  items = get_consumables()
  return next((it for it in items if it['MItemId'] == id), None)

def get_gear_stock(id):
  items = get_gears()
  return next((it for it in items if it['MCharacterPieceId'] == id), None)

def get_mistgear_stock(num_only=False):
  ret = get_consumable_stock(MIST_GEAR_ID)
  return ret['Stock'] if num_only else ret

def get_item_stock(item, num_only=False):
  '''
  If `num_only=True`, will only return an `int` that indicates the amount possessed 
  '''
  ret = None
  kit = 'ItemType'
  kid = 'ItemId'
  if item[kit] == ITYPE_GOLD:
    ret = deepcopy(item)
    ret['Stock'] = get_profile()['Money']
  elif item[kit] in [ITYPE_GEAR, ITYPE_GEAR2]:
    ret = get_gear_stock(item[kid])
    if not ret:
      return None
    ret[kit] = ITYPE_GEAR
  elif item[kit] == ITYPE_CONSUMABLE:
    ret = get_consumable_stock(item[kid])
    if not ret:
      return None
    ret[kit] = ITYPE_CONSUMABLE
  return ret['Stock'] if num_only else ret

def sell_consumable(item, amount):
  global __UnsellableItems
  uid = item['Id']
  if uid in __UnsellableItems:
    return None
  res = game.post_request(f"/api/UItems/{uid}/sell/{amount}")
  if not res:
    log_warning(f"Unsellable {item}")
    __UnsellableItems.add(uid)
    return None
  return res['r']

def sell_gear(item, amount):
  uid = item['UCharacterPieceId']
  res = game.post_request(f"/api/UCharacterPieces/{uid}/trade/{amount}")
  return res['r']['Items']

def sell_item(item, amount=1):
  if item['ItemType'] in [ITYPE_GEAR, ITYPE_GEAR2]:
    return sell_gear(item, amount)
  elif item['ItemType'] == ITYPE_CONSUMABLE:
    gain = sell_consumable(item, amount)
    if not gain:
      return None
    return [{'ItemType': ITYPE_GOLD, 'ItemId': 0, 'ItemQuantity': gain, 'Stock': gain}]

def exchange_bets(amount=0, budget=0):
  '''
  amount: Bets amount to exchange
  budget: Gold amount to exchange bets (20:1)
  '''
  if budget:
    amount = budget // 20
  res = game.post_request(f"/api/Casino/ExchangeCoin?exchangeGolds={amount}")
  return res['r']

def get_suitable_equpiments(character, slot_idx):
  global SWAP_GEAR_ID
  key_chb = 'MCharacterBase'
  key_wp  = 'WeaponEquipType'
  if key_chb in character:
    wtype = character[key_chb][key_wp]
  elif 'MCharacter' in character:
    wtype = character['MCharacter'][key_chb][key_wp]
  else:
    return get_suitable_equpiments(game.get_character_base(character['MCharacterId']), slot_idx)
  ret_wp = None
  ret_ar = None
  ret_ac = None
  equips = SWAP_GEAR_ID[slot_idx]
  ret_wp = equips['weapon'][wtype]
  ret_ar = equips['armor']
  ret_ac = equips['accessory']
  return [ret_wp, ret_ar, ret_ac]

def swap_party_character(pid, sidx, cid, **kwargs):
  '''
  Arguments:
  `pid`: Party id
  `sidx`: Slot index
  `cid`: (U)Character id to swap (to the given index)
 
  Kwargs:
  `pidx=int`: Party index, will use this if pid is not given
  `wid=None`: Weapon id
  `aid=None`: Armor id
  `did=None`: Decoration(Accessory) id
  `eid=None`: Extra skill id
  '''
  wid = kwargs.get('wid')
  aid = kwargs.get('aid')
  did = kwargs.get('did')
  eid = kwargs.get('eid')
  pidx = kwargs.get('pidx')
  if not eid:
    eid = 'null'
  
  parties = get_current_parties()['UParties']
  if not pidx:
    pidx = next((p['PartyNo']-1 for p in parties if p['Id'] == pid), None)
  party = get_current_parties()['UParties'][pidx]
  sid = party['UCharacterSlots'][sidx]['Id']
  char = get_character_by_uid(cid)
  equips = get_suitable_equpiments(char, sidx)
  if not wid:
    wid = equips[0] or 'null'
  if not aid:
    aid = equips[1] or 'null'
  if not did:
    did = equips[2] or 'null'
  return game.post_request(f"/api/UParties/{pid}/CharacterSlots/{sid}?uCharacterId={cid}&uWeaponId={wid}&uArmorId={aid}&uAccessoryId={did}&uSkillId={eid}")

def get_character_party_index(pid, mchid):
  party = get_party_by_pid(pid)
  ch_bname = game.get_character_name(mchid).split(']')[-1]
  for s in party['UCharacterSlots']:
    mid = s['UCharacter']['MCharacterId']
    if game.get_character_name(mid).split(']')[-1] == ch_bname:
      return s['SlotNo'] - 1
  return None

def enhance_abstone_def(id, n1=0, n2=0, n3=0):
  data = {
    'MItemIdAmount': {}
  }
  if n1:
    data['MItemIdAmount'][13] = n1
  if n2:
    data['MItemIdAmount'][14] = n2
  if n3:
    data['MItemIdAmount'][15] = n3
  return game.post_request(f"/api/UAbilityStones/{id}/enhance", data)

def enhance_abstone_atk(id, n1=0, n2=0, n3=0):
  data = {
    'MItemIdAmount': {}
  }
  if n1:
    data['MItemIdAmount'][10] = n1
  if n2:
    data['MItemIdAmount'][11] = n2
  if n3:
    data['MItemIdAmount'][12] = n3
  return game.post_request(f"/api/UAbilityStones/{id}/enhance", data)

def dump_scene_metadata():
  uris = {
    'main': '/api/UScenes/MainScenes',
    'event': '/api/UScenes/EventScenes',
  }
  ret = {}
  for key,uri in uris.items():
    res = game.get_request(uri)
    data = res['r']
    with open(f"{DCTmpFolder}/{SCENE_METAS[key]}", 'w') as fp:
      json.dump(data, fp, indent=2)
      ret[key] = data
    log_info(f"{key} scene meta saved")
  return ret

def dump_all_available_scenes(meta):
  for chapter in meta:
    for inf in chapter['Scenes']:
      id = inf['MSceneId']
      epilogue = inf['MSceneId'] % 100 > 10
      if not inf['Status'] and not epilogue:
        log_warning(f"Scene#{id} {game.get_scene(id)['Title']} not unlocked yet, skip")
        continue
      path = f"{DCTmpFolder}/scenes/{id}.json"
      if os.path.exists(path):
        log_info(f"Scene#{id} {game.get_scene(id)['Title']} already saved, skip")
        continue
      res = game.get_request(f"/api/UScenes/{id}")
      data = res['r']
      data['MSceneDetailViewModel'] = sorted(data['MSceneDetailViewModel'], key=lambda o:o['GroupOrder'])
      with open(path, 'w') as fp:
        json.dump(data, fp)
      log_info(f"Scene#{id} {game.get_scene(id)['Title']} saved")

def vote_character(event_id, character_id):
  if not VoteItemId or VoteItemId not in ConsumableInventory:
    log_warning("Vote item unavailable")
    return 0
  total = 0
  while ConsumableInventory[VoteItemId] > 0:
    n = min(ConsumableInventory[VoteItemId], 99999)
    ConsumableInventory[VoteItemId] -= n
    total += n
    res = game.post_request(f"/api/Vote/Vote/{event_id}/{character_id}/{n}")
    log_info(f"Voted {n}, response:", res)
  return total