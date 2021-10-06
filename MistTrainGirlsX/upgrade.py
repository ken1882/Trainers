from _G import *
import json

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}
MaxExpLevel  = 50
MaxGearLevel = 20

def get_characters():
  res = Session.get('https://mist-train-east4.azurewebsites.net/api/UCharacters')
  if not is_response_ok(res):
    return []
  return res.json()['r']

def get_layer_gears(mchid):
  res = Session.get(f"https://mist-train-east4.azurewebsites.net/api/UCharacters/LimitBreakPieces/{mchid}")
  if not is_response_ok(res):
    return None
  return res.json()['r']['CurrentPieces']

def bulk_enhance(chid, lv=None, lgn=None, mgn=None, kp=None):
  if all([ not k for k in [lv,lgn,mgn,kp] ] ):
    log_info("No bulk enhance items assigned")
    return
  gear_dat = None
  if lgn or mgn:
    lgn = lgn or 0
    mgn = mgn or 0
    gear_dat = {
      "LayerGearQuantity": lgn,
      "MistGearQuantity": mgn
    }
  res = Session.post(f"https://mist-train-east4.azurewebsites.net/api/UCharacters/BulkEnhance/{chid}", json.dumps({
    "UCharacterLevelupModel": lv,
    "GearPointAddModel": gear_dat,
    "KizunaPointAddModel": kp,
  }), headers=Headers)
  if not is_response_ok(res):
    return (None,None,None)
  rjs = res.json()['r']['UCharacterViewModel']
  return (rjs['Level'], rjs['GearLevel'], rjs['KizunaRank'])

def level_up(chid,level=1):
  can_lvup = True
  while can_lvup and level < MaxExpLevel:
    level += 1
    res = Session.post(f"https://mist-train-east4.azurewebsites.net/api/UCharacters/Levelup/{chid}/{level}")
    if not is_response_ok(res):
      break
    can_lvup = res.json()['r']['UCharacterViewModel']['CanLevelup']
  return level

def do_enhance(character):
  chid  = character['Id']
  mchid = character['MCharacterId']
  log_info("Enhancing character of id", chid)
  lgn = get_layer_gears(mchid)
  log_info("Layer gears:", lgn)
  if lgn > 0 and character['GearLevel'] < MaxGearLevel:
    elv,glv,klv = bulk_enhance(chid, lgn=lgn)
    log_info(f"Enhance done; Gear Level={glv}")
  if character['CanLevelup']:
    lv = level_up(chid, character['Level'])
    log_info(f"Levelup complete, current level={lv}")

def enhance_all_characters():
  ar = get_characters()
  for i,ch in enumerate(ar):
    do_enhance(ch)
    log_info(f"Progress: {i+1}/{len(ar)}")
    uwait(0.5)
  log_info("Upgrade completed")