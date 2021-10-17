from _G import *
import game
import player

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}
MaxExpLevel  = 50
MaxGearLevel = 20
MaxKizunaPoint = 1300
TotalKizunaPoint = [0, 0, 100, 250, 400, 550, 700, 850, 1000, 1150, 1300]

def get_layer_gears(mchid):
  res = game.get_request(f"https://mist-train-east4.azurewebsites.net/api/UCharacters/LimitBreakPieces/{mchid}")
  return res['r']['CurrentPieces']

def get_kizuna(uid):
  res = game.get_request(F"https://mist-train-east4.azurewebsites.net/api/Kizuna/{uid}")
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
      "LayerGearQuantity": lgn,
      "MistGearQuantity": mgn
    }
  payload = {
    "UCharacterLevelupModel": lv,
    "GearPointAddModel": gear_dat,
    "KizunaPointAddModel": kp,
  }
  log_debug("Request payload:\n", payload)
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/UCharacters/BulkEnhance/{chid}", payload)
  if not res:
    return (None,None,None)
  rjs = res['r']['UCharacterViewModel']
  return (rjs['Level'], rjs['GearLevel'], rjs['KizunaRank'])

def level_up(chid,level=1):
  can_lvup = True
  while can_lvup and level < MaxExpLevel:
    level += 1
    res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/UCharacters/Levelup/{chid}/{level}")
    if not res:
      break
    can_lvup = res['r']['UCharacterViewModel']['CanLevelup']
    uwait(0.1)
  return level

def do_enhance(character):
  chid  = character['Id']
  mchid = character['MCharacterId']
  log_info("Enhancing character of id", chid)
  lgn = get_layer_gears(mchid)
  log_info("Layer gears:", lgn)
  kp  = determine_kizuna_usage(get_kizuna(chid))
  if kp:
    log_info("Kizuna usage:", kp)
    kp = {'MKizunaItemIdAmount': kp}
  else:
    kp = None
  if kp or (lgn > 0 and character['GearLevel'] < MaxGearLevel):
    if not lgn or character['GearLevel'] == MaxGearLevel:
      lgn = None
    elv,glv,klv = bulk_enhance(chid, lgn=lgn, kp=kp)
    log_info(f"Enhance done; Gear Level={glv}; Kizuna Level={klv}")
  if character['CanLevelup']:
    lv = level_up(chid, character['Level'])
    log_info(f"Levelup complete, current level={lv}")

def enhance_all_characters():
  ar = player.get_characters()
  for i,ch in enumerate(ar):
    do_enhance(ch)
    log_info(f"Progress: {i+1}/{len(ar)}")
    uwait(0.3)
  log_info("Upgrade completed")

def main():
  enhance_all_characters()

if __name__ == '__main__':
  main()