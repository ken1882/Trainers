import _G
from _G import *
import itertools
import pprint
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
import player
import friend
import discord
import Input
import game
import win32con
import utils
from stage import StageAlias

LOG_STATUS = True

PartyId  = 0
StageId  = 0
BattleId = 0
RentalUid = 0
BattleStyle = [ # 0=通常 1=限制 2=全力 3=使用最低熟練度
  0, # reserved, don't touch
  3,
  3,
  3,
  3,
  3,
]

RecoveryUsage = 1 # 0=Use most
                  # 1=Use by the order list below, if item available
RecoveryUsageOrder = [
  424, 427, 5,
  0 # use most
]
RecoveryBatchAmount = 5 # How many items to use once

AutoSellItems = [
  #             type     Id  Maximum keep  Minimum keep
  (       ITYPE_GEAR,   106,          500,          100), # Gear：[古の魔女の末裔]セイラム
  ( ITYPE_CONSUMABLE,     7,        99900,        99000), # Small cake
  ( ITYPE_CONSUMABLE,    10,        99000,        99000), # A Weapon enhance material
  ( ITYPE_CONSUMABLE,    11,        99900,        99000)  # S Weapon enhance material
]


UnmovableEffects = [22,23]
MaxSP = 20
MaxOP = 100
MaxProficiency = 99

LastBattleWon = False
FlagRequestReEnter = False

AvailableFriendRentals = []
RentalCycle = None

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}

def start_battle(sid, pid, rid=0):
  log_info("Staring batlle")
  rid = rid if rid else 'null'
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/canstart/{sid}?uPartyId={pid}")
  if res['r']['FaildReason'] != ERROR_SUCCESS:
    return res['r']['FaildReason']
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/start/{sid}?uPartyId={pid}&rentalUUserId={rid}&isRaidHelper=null&uRaidId=null&raidParticipationMode=null")
  return res['r']

def process_actions(commands):
  log_info("Process actions")
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/attack/{BattleId}",
    {
      "Type":1,
      "IsSimulation": False,
      "BattleSettings": {
        "BattleAutoSetting":3,
        "BattleSpeed":2,
        "BattleSpecialSkillAnimation":0,
        "IsAutoSpecialSkill":False,
        "IsAutoOverDrive":True,
        "EnableConnect":True
      },
      "Commands": commands
    }
  )
  return res['r']

def surrender():
  log_info("Abort battle")
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/surrender",
    {
      "Type":1,
      "IsSimulation": False,
      "BattleSettings": {
        "BattleAutoSetting":3,
        "BattleSpeed":2,
        "BattleSpecialSkillAnimation":0,
        "IsAutoSpecialSkill":False,
        "IsAutoOverDrive":True,
        "EnableConnect":True
      },
    }
  )
  return res['r']

def get_alive_characters(characters):
  ret = []
  for ch in characters:
    if ch["HP"] <= 0:
      continue
    ret.append(ch)
  return ret

def get_movable_characters(characters):
  ret = []
  for ch in characters:
    if ch["HP"] <= 0:
      continue
    if any([ stat["SkillEffectType"] in UnmovableEffects for stat in ch["Auras"] ]):
      continue
    ret.append(ch)
  return ret

def is_skill_usable(character, skill):
  sp = character['SP']
  rp = character['RP']
  if sp < skill['SPCost'] or rp < skill['RPCost']:
    return False
  return True

def is_offensive_skill(skill):
  return skill['SkillCategory'] == SSCOPE_ENEMY

def get_least_proficient_skill(character, skills):
  mcharacter = player.get_character_by_uid(character['CID'])
  uskills = [mcharacter['USkill1'], mcharacter['USkill2'], mcharacter['USkill3']]
  luskill = sorted(uskills, key=lambda sk:sk['Rank'])[0]
  if luskill['Rank'] == MaxProficiency:
    return None
  return next((sk for sk in skills if sk['Id'] == luskill['Id']), None)

def determine_skill(character):
  skills = []
  for sk in character['Skills']:
    if not sk['IsCommandSkill']:
      continue
    if (sk['Id'] <= 0 or sk['SP'] <= 0) and sk['SkillType'] != STYPE_NORMAL_ATTACK:
      continue
    skills.append(sk)
  skills = sorted(skills, key=lambda s:s['SP'])
  bstyle = BattleStyle[character['ID']]
  if bstyle == 0: # Normal attack only
    return skills[0]
  if bstyle == 3:
    skill = get_least_proficient_skill(character, skills)
    if skill: # Act like BattleStyle=2 if all skills are mastered
      if is_skill_usable(character, game.get_skill(skill['SkillRefId'])):
        return skill
      return skills[0]
  for sk in reversed(skills):
    mskill = game.get_skill(sk['SkillRefId'])
    if not is_offensive_skill(mskill):
      continue
    elif is_skill_usable(character, mskill):
      return sk
    elif bstyle == 1:
      break # only use most powerful offensive skill
  return skills[0] # normal attack

def determine_target(skill, enemies, characters):
  mskill = game.get_skill(skill['SkillRefId'])
  if is_offensive_skill(mskill):
    return enemies[0]['ID']
  return sorted(characters, key=lambda ch:ch['HP'])[0]['ID']

def determine_actions(data):
  charcaters = get_movable_characters(data['BattleState']['Characters'])
  ret = []
  for ch in charcaters:
    skill = determine_skill(ch)
    ret.append({
      'UnitSerialId': ch['ID'],
      'TargetId': determine_target(skill, data['BattleState']['Enemies'], charcaters),
      'CommandId': skill['Id'],
      'IsOverDrive': ch['OP'] >= 100
    })
  return ret

def sell_surplus_loots(loots):
  global AutoSellItems
  for item in AutoSellItems:
    type = item[0]
    id   = item[1]
    loot = next((it for it in loots if not it['Sold'] and it['ItemType'] == type and id == it['ItemId']), None)
    if not loot:
      continue
    maxn = item[2]
    minn = item[3]
    sitem = player.get_stock_item(loot)
    if not sitem:
      continue
    sitem['ItemType'] = type
    curn = sitem['Stock']
    if curn <= maxn:
      continue
    player.sell_item(sitem, curn-minn)
    log_info(f"Sold item {game.get_item_name(loot)}, amount={curn-minn}")

def process_victory():
  global LastBattleWon
  log_info("Victory")
  LastBattleWon = True
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Battle/victory?isSimulation=false')
  return res['r']

def process_defeat():
  global LastBattleWon
  log_info("Defeat")
  LastBattleWon = False
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Battle/defeat?isSimulation=false')
  return res['r']

def recover_stamina():
  items = player.get_aprecovery_items()
  log_info("Recovery items:", pprint.pformat(items, indent=2), '-'*21, sep='\n')
  items = sorted(items, key=lambda i:i['Stock'])
  nidx  = -1
  if RecoveryUsage == 1:
    for id in RecoveryUsageOrder:
      if id == 0:
        nidx = -1
        break
      nidx = next((i for i,item in enumerate(items) if item["MItemId"] == id), -1)
      nidx = -1 if items[nidx]['Stock'] <= 0 else nidx
      if nidx >= 0:
        break
    
  item = items[nidx]
  num  = min(RecoveryBatchAmount, item['Stock'])
  res = player.use_aprecovery_item(item, num)
  if not res:
    log_error("Out of stamina, aborting")
    exit()
  log_info(f"Recovey {item} used, stock left: {item['Stock']-num}")
  log_info("Current stamina:", res['r']['CurrentStamina'])

def log_battle_status(data, actions=[]):
  if not LOG_STATUS or VerboseLevel < 3:
    return
  try:
    string  = '\n========== Status ==========\n'
    string += f"Wave#{data['BattleState']['WaveNumber']} Turn#{data['BattleState']['TurnNumber']}\n"
    string += "***** Players *****\n"
    for idx,ch in enumerate(data['BattleState']['Characters']):
      actor = player.get_character_by_uid(ch['CID'])
      bchar = game.get_character_base(actor['MCharacterId'])
      string += f"{bchar['Name']} {bchar['MCharacterBase']['Name']}\n"
      hps = f"HP: {ch['HP']}/{actor['UCharacterBaseViewModel']['Status']['HP']}"
      sps = f"SP: {ch['SP']}/{MaxSP}"
      ops = f"OP: {ch['OP']}/{MaxOP}"
      rps = f"RP: {ch['RP']}/{ch['MaxRP']}"
      string += "{:15} {:8} {:10} {:8}\n".format(hps, sps, ops, rps)
      action  = next((act for act in actions if act['UnitSerialId'] == ch['ID']), None)
      if action:
        act = action['CommandId']
        if act < 0:
          action = '通常攻撃'
        else:
          act = next((sk for sk in ch['Skills'] if sk['Id'] == act), None)
          act = game.get_skill(act['SkillRefId']) if act else ''
          action = act['Name'] if act else ''
      elif ch['HP'] == 0:
        action = '戦闘不能'
      elif 'BattleActions' in data:
        action = '行動不能'
      string += f"Action: {action}\n" if action else ''
      # string += '-----\n'
    string += "\n***** Enemies *****\n"
    for ch in data['BattleState']['Enemies']:
      name = game.get_enemy(ch['EID'])['Name']
      string += f"{name} (HP:{ch['CurrentHPPercent']}%)"
      if 'BattleActions' in data:
        action = next((act for act in data['BattleActions'] if act['ActorId'] == ch['ID']), None)
        if action and action['SkillId']:
          action = game.get_skill(action['SkillId'])
          string += f" Action: {action['Name']}"
      string += '\n'
      # string +='-----\n'
    string += "===============================\n"
    log_info(string)
  except Exception as err:
    log_error("Error occurred during loggin battle status:", handle_exception(err))

def log_loots(data):
  if not LOG_STATUS or VerboseLevel < 3:
    return
  string  = '\n' + '='*31 + ' Loots ' + '='*31 + '\n'
  for loot in data:
    if loot['ItemType'] == ITYPE_GOLD:
      string += f"Gold: {loot['ItemQuantity']}\n"
      continue
    name = game.get_item_name(loot)
    string += f"{name} x{loot['ItemQuantity']}\n"
  string += '='*69 + '\n'
  log_info(string)

def log_player_profile(data):
  if not LOG_STATUS or VerboseLevel < 3:
    return
  string  = '\n===== Player Info =====\n'
  string += f"Level: {data['Level']}\n"
  string += f"Exp: {data['TotalExperience']}\n"
  string += f"Gold: {data['Money']}\n"
  string += f"Stamina: {data['CurrentActionPoints']} / {data['MaxActionPoints']}\n"
  string += "=======================\n"
  log_info(string)

def is_defeated(data):
  return len(get_alive_characters(data['BattleState']['Characters'])) == 0

def process_combat(data):
  global LastBattleWon
  LastBattleWon = False
  log_info("Battle started")
  log_battle_status(data)
  player.clear_cache()
  while not is_defeated(data) and data['BattleState']['BattleStatus'] != BATTLESTAT_VICTORY:
    actions = determine_actions(data)
    data = process_actions(actions)
    log_battle_status(data, actions)
    uwait(0.3)
    if _G.Throttling:
      uwait(1)
  if is_defeated(data):
    process_defeat()
  else:
    res = process_victory()
    log_loots(res['QuestLoots']['Items'])
    sell_surplus_loots(res['QuestLoots']['Items'])
    log_player_profile(res['UUser'])
    discord.update_player_profile(res['UUserPreferences']['Name'], res['UUser']['Level'])
  return LastBattleWon

def process_partyid_input():
  pid = 0
  while pid not in range(1,11):
    try:
      pid = int(input("Party number (0 for list your parties): "))
    except Exception:
      pid = 0
    if pid == 0:
      player.log_party_status()
  pid = next((p['Id'] for p in player.get_current_parties()['UParties'] if p['PartyNo'] == pid), None)
  return pid

def process_stageid_input():
  sid = 0
  while not sid:
    sid = input("Stage id: ")
    if not utils.isdigit(sid):
      if sid in StageAlias:
        sid = StageAlias[sid]
      else:
        continue
    sid = int(sid)
  return sid

def process_rentalid_input():
  global AvailableFriendRentals,RentalCycle
  rid = 0
  valids = []
  pdat,odat = friend.get_rentals()
  for dat in pdat:
    uid = dat['UUserId']
    valids.append(uid)
    AvailableFriendRentals.append(uid)
  for dat in odat:
    valids.append(dat['UUserId'])
  while rid not in valids and rid != -1:
    try:
      rid = int(input("Rental friend's id (0 for list availables, -1 for round-robin): "))
    except Exception:
      rid = 0
    if not rid:
      friend.log_rentals(True)
  RentalCycle = itertools.cycle(AvailableFriendRentals)
  return rid

def start_battle_process(sid, pid, rid):
  global BattleId,LastErrorCode
  log_info("Stage/Party/Rental IDs:", sid, pid, rid)
  data = start_battle(sid, pid, rid)
  if type(data) == int:
    if data == ERROR_NOSTAMINA:
      log_info("Recover Stamina")
      recover_stamina()
      data = start_battle(sid, pid, rid)
  if type(data) == dict and 'BattleId' in data:
    BattleId = data['BattleId']
    return process_combat(data)
  else:
    LastErrorCode = data
    raise RuntimeError(f"Unable to start battle (ERRNO={data})")

def update_input():
  global FlagRunning,FlagPaused,FlagRequestReEnter
  Input.update()
  if Input.is_trigger(win32con.VK_F7):
    FlagPaused ^= True
    print("Worker", 'paused' if FlagPaused else 'unpaused')
  elif Input.is_trigger(win32con.VK_F8):
    FlagRunning = False
  elif Input.is_trigger(win32con.VK_F5):
    FlagRequestReEnter = True

def process_prepare_inputs():
  pid = process_partyid_input()
  log_info("Party Id:", PartyId)
  sid = process_stageid_input()
  rid = process_rentalid_input()
  log_info("Rental Id:", 'Round-Robin' if rid == -1 else rid)
  if rid != -1 and rid <= 0:
    rid = 'null'
  return (pid, sid, rid)

def main():
  global PartyId,StageId,RentalUid,AvailableFriendRentals,RentalCycle
  global FlagRunning,FlagPaused,FlagRequestReEnter
  PartyId,StageId,RentalUid = process_prepare_inputs()
  discord.update_status(StageId)
  cnt = 0
  while FlagRunning:
    while FlagPaused:
      update_input()
      wait(0.1)
    if FlagRequestReEnter:
      PartyId,StageId,RentalUid = process_prepare_inputs()
      discord.update_status(StageId)
      FlagRequestReEnter = False
      cnt = 0
    cnt += 1
    log_info(f"Running combat iteration#{cnt}")
    rid = RentalUid
    if rid == -1:
      rid = next(RentalCycle)
    start_battle_process(StageId, PartyId, rid)
    log_info("Battle Ended")
    uwait(1)
    if _G.Throttling:
      uwait(1)
    update_input()

if __name__ == '__main__':
  try:
    game.init()
    main()
    FlagRunning = False
  except (SystemExit, KeyboardInterrupt):
    if LastErrorCode == 403:
      discord.update_status(0)
    exit()