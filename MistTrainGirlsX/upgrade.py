from requests import exceptions
from _G import *
import game
import player
import math
import mtg_parser

TargetGearLevel  = 20
MinMistGearKeep = 1000000

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}
MaxExpLevel  = 50
MaxGearLevel = 20
MaxKizunaPoint = 1300
CharacterPieceExp = {
  RARITY_A:   200,
  RARITY_S:   600,
  RARITY_SS: 1000,
}
TotalKizunaPoint = [0, 0, 100, 250, 400, 550, 700, 850, 1000, 1150, 1300]
MistGearStockCache = -1

WEAPON_BULK_MATERIALS = [
  {},
  {},
  {},
  {
    "EvolutionUpCount":3,
    "BulkEnhanceOrders":[
      {
        "Order":3,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":13}]
      },
      {
        "Order":2,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":9}]
      },
      {
        "Order":1,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":6}]
      },
      {
        "Order":0,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":5}]
      }
    ]
  },
  {
    "EvolutionUpCount":4,
    "BulkEnhanceOrders":[
      {
        "Order":4,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":26}]
      },
      {
        "Order":3,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":13}]
      },
      {
        "Order":2,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":9}]
      },
      {
        "Order":1,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":6}]
      },
      {
        "Order":0,
        "EnhanceMItemIdAmounts":[{"MItemId":11,"Amount":5}]
      }
    ]
  }
]

def get_layer_gears(mchid):
  res = game.get_request(f"/api/UCharacters/LimitBreakPieces/{mchid}")
  return res['r']['CurrentPieces']

def get_kizuna(uid):
  res = game.get_request(F"/api/Kizuna/{uid}")
  return res['r']

def determine_kizuna_usage(kdat):
  left = MaxKizunaPoint - TotalKizunaPoint[kdat['CurrentKizunaRank']] - kdat['CurrentKizunaPoint']
  ret = {}
  for i in kdat['Items']:
    n = min(i['Stock'], left // i['Point'])
    if n == 0:
      continue
    ret[i['MItemId']] = n
    left -= n*i['Point']
    if left == 0:
      break
  return ret

def bulk_enhance(chid, lv=None, lgn=None, mgn=None, kp=None):
  if all([ not k for k in [lv,lgn,mgn,kp] ] ):
    log_info("No bulk enhance items assigned")
    return
  gear_dat = None
  if lgn or mgn:
    lgn = lgn or 0
    mgn = mgn or 0
    gear_dat = {
      "AttributeGearMitemId": None,
      "AttributeGearQuantity": 0,
      "LayerGearQuantity": lgn,
      "MistGearQuantity": mgn
    }
  payload = {
    "UCharacterLevelupModel": lv,
    "GearPointAddModel": gear_dat,
    "KizunaPointAddModel": kp,
  }
  log_debug("Request payload:\n", payload)
  res = game.post_request(f"/api/UCharacters/BulkEnhance/{chid}", payload)
  if not res:
    return (None,None,None)
  rjs = res['r']['UCharacterViewModel']
  return (rjs['Level'], rjs['GearLevel'], rjs['KizunaRank'])

def level_up(chid,level=1):
  can_lvup = True
  while can_lvup and level < MaxExpLevel:
    level += 1
    res = game.post_request(f"/api/UCharacters/Levelup/{chid}/{level}")
    if not res:
      break
    can_lvup = res['r']['UCharacterViewModel']['CanLevelup']
    uwait(0.1)
  return level

def enhance_gear(character, target_lv):
  global MistGearStockCache
  if MistGearStockCache == -1:
    MistGearStockCache = player.get_mistgear_stock(True)
  mchid = character['MCharacterId']
  cur = character['TotalGearExperience']
  lgn = get_layer_gears(mchid)
  rarity = game.get_character_base(mchid)['CharacterRarity']
  if cur >= game.GearProgressionTable[rarity][MaxGearLevel]:
    log_info("Max gear level reached")
    return MaxGearLevel
  needed_max    = game.GearProgressionTable[rarity][MaxGearLevel] - cur
  needed_target = game.GearProgressionTable[rarity][target_lv] - cur
  lgxp = CharacterPieceExp[rarity]
  lgn = min(lgn, math.ceil(needed_max / lgxp))
  needed_max = needed_max - lgn * lgxp
  needed_target = max(needed_target - lgn * lgxp, 0)
  mgn = 0 if MistGearStockCache - needed_target < MinMistGearKeep else needed_target
  if mgn + lgn == 0:
    log_info("Insufficient gear to enhance" if needed_target > 0 else 'Target gear level already reached')
    return character['GearLevel']
  MistGearStockCache -= mgn
  log_info(f"Enhancing character with pieces x{lgn} and mist gear x{mgn}")
  gear_dat = {
    "AttributeGearMitemId": None,
    "AttributeGearQuantity": 0,
    "LayerGearQuantity": lgn,
    "MistGearQuantity": mgn
  }
  res = game.post_request(f"/api/UCharacters/AddGearPoint/{character['Id']}", gear_dat)
  log_info("Gear level enhance done, mist gear left:", MistGearStockCache)
  return res['r']['CurrentGearLevel']

def do_enhance(character, target_lv=None):
  global TargetGearLevel
  if not target_lv:
    target_lv = TargetGearLevel
  chid  = character['Id']
  log_info("Enhancing ", game.get_character_name(character['MCharacterId']))
  kp  = determine_kizuna_usage(get_kizuna(chid))
  if kp:
    log_info("Kizuna usage:", kp)
    kp = {'MKizunaItemIdAmount': kp}
  else:
    kp = None
  if character['CanLevelup']:
    lv = level_up(chid, character['Level'])
    log_info(f"Levelup complete, current level={lv}")
  if character['GearLevel'] < MaxGearLevel:
    res = enhance_gear(character, target_lv)
    log_info(f"Gear enhance complete, current level={res}")
  else:
    log_info("Character already reached max gear level")
  if kp:
    elv,glv,klv = bulk_enhance(chid, kp=kp)
    log_info(f"Enhance done; Level={elv}; Gear Level={glv}; Kizuna Level={klv}")

def enhance_all_characters(glv=0):
  ar = player.get_characters()
  for i,ch in enumerate(ar):
    do_enhance(ch, glv)
    log_info(f"Progress: {i+1}/{len(ar)}")
    uwait(0.3)
  log_info("Upgrade completed, mist gear left:", MistGearStockCache)


def enhance_all_abstone(na, ns, nss=0):
  inventory = player.get_all_items()
  items = inventory[ITYPE_ABSTONE]
  resources = {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
  res = game.get_request('/api/UItems/WeaponEnhanceItems')
  for i in res['r']:
    resources[i['MItemId']] = i['Stock']
  res = game.get_request('/api/UItems/ArmorEnhanceItems')
  for i in res['r']:
    resources[i['MItemId']] = i['Stock']
  for item in items:
    if not item['CanLevelUp'] or item['Level'] >= 5:
      continue
    name = game.get_item_name(item)
    log_info("Enhancing", name)
    if '戦' in name:
      if 'SS' in name:
        if resources[10] < na or resources[11] < ns or resources[12] < nss:
          log_warning("Insufficient resources to enhance weapon, skipped")
          continue
        print(player.enhance_abstone_atk(item['Id'], na, ns, nss))
        resources[10] -= na
        resources[11] -= ns
        resources[12] -= nss
    elif '守'in name:
      if 'SS' in name:
        if resources[13] < na or resources[14] < ns or resources[15] < nss:
          log_warning("Insufficient resources to enhance armor, skipped")
          continue
        print(player.enhance_abstone_def(item['Id'], na, ns, nss))
        resources[13] -= na
        resources[14] -= ns
        resources[15] -= nss

def enhance_all_weapons():
  items = player.get_all_items()[ITYPE_WEAPON]
  for item in items:
    if item['TotalExperience'] > 0 or not item['CanLevelup']:
      continue
    bitem = game.get_item(item)
    log_info("Enhancing", bitem['Name'])
    rarity = bitem['EquipmentRarity']
    data = WEAPON_BULK_MATERIALS[rarity]
    try:
      print(game.post_request(f"/api/UWeapons/{item['Id']}/bulkEnhance", data))
    except (Exception,SystemExit) as err:
      log_error(err)
      break

def enhance_lb_level(uchid, amount):
  return game.post_request(
    f"/api/UCharacters/LevelLimitBreak/Enhance/{uchid}",
    mtg_parser.parse_lblevelup_payload({
      'CharacterExperienceItemQuantity': 0,
      'Experience': amount,
      'GeneralExperienceItemQuantity': 0,
    })
  )

def enhance_pt(uid, insurance=False, itype=0):
  if itype == 0:
    itype = 64
  try:
    return game.post_request(
      f"https://mist-train-east5.azurewebsites.net/api/UFieldSkills/{uid}/enhance", 
      {"UseInsurance": insurance, "MItemId": itype}
    )
  except (Exception, SystemExit) as err:
    handle_exception(err)
    return False

def main():
  enhance_all_characters()

if __name__ == '__main__':
  game.init()
  main()