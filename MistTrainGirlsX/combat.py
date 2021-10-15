from _G import *
import pprint
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
import player
import friend
import discord

PartyId  = 0
StageId  = 0
BattleId = 0
RentalUid = 0
BattleStyle = [ # 0=通常 1=限制 2=全力
  0, # reserved, don't touch
  2,
  2,
  2,
  2,
  1,
]
RecoveryUsage = 424 # 0=Use most, others=Use with that item id if exists
RecoveryBatchAmount = 5 # How many items to use once
UnmovableEffects = [22,23]
MaxSP = 20
MaxOP = 100

LOG_STATUS = True

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}

def start_battle():
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/canstart/{StageId}?uPartyId={PartyId}")
  if res['r']['FaildReason'] != ERROR_SUCCESS:
    return res['r']['FaildReason']
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/start/{StageId}?uPartyId={PartyId}&rentalUUserId={RentalUid}&isRaidHelper=null&uRaidId=null&raidParticipationMode=null")
  return res['r']

def process_actions(commands):
  log_info("Process actions")
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/attack/{BattleId}",
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
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/surrender",
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

def determine_skill(character):
  skills = []
  for sk in character['Skills']:
    if not sk['IsCommandSkill']:
      continue
    if (sk['Id'] <= 0 or sk['SP'] <= 0) and sk['SkillType'] != STYPE_NORMAL_ATTACK:
      continue
    skills.append(sk)
  skills = sorted(skills, key=lambda s:s['SP'])
  for sk in reversed(skills):
    mskill = get_skill(sk['SkillRefId'])
    if not is_offensive_skill(mskill):
      continue
    elif is_skill_usable(character, mskill):
      return sk['Id']
    elif BattleStyle[character['ID']] == 1:
      break # only use most powerful offensive skill
  return skills[0]['Id'] # normal attack

def determine_target(enemies):
  return enemies[0]['ID']

def determine_actions(data):
  charcaters = get_movable_characters(data['BattleState']['Characters'])
  ret = []
  for ch in charcaters:
    ret.append({
      'UnitSerialId': ch['ID'],
      'TargetId': determine_target(data['BattleState']['Enemies']),
      'CommandId': determine_skill(ch),
      'IsOverDrive': ch['OP'] >= 100
    })
  return ret

def process_victory():
  log_info("Victory")
  res = post_request('https://mist-train-east4.azurewebsites.net/api/Battle/victory?isSimulation=false')
  return res['r']

def process_defeat():
  log_info("Defeat")
  res = post_request('https://mist-train-east4.azurewebsites.net/api/Battle/defeat?isSimulation=false')
  return res['r']

def recover_stamina():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/UItems/ApRecoveryItems')
  items = res['r']
  log_info("Recovery items:", pprint.pformat(items, indent=2), '-'*21, sep='\n')
  items = sorted(items, key=lambda i:i['Stock'])
  nidx  = -1
  if RecoveryUsage != 0:
    nidx = next((i for i,item in enumerate(items) if item["MItemId"] == RecoveryUsage), -1)
    nidx = -1 if items[nidx]['Stock'] <= 0 else nidx
  nid = items[nidx]['MItemId']
  num = min(RecoveryBatchAmount, items[nidx]['Stock'])
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/Users/recoverStamina/{nid}/{num}")
  log_info(f"Recovey item@{nid} used, stock left: {items[nidx]['Stock']-num}")
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
      bchar = get_character_base(actor['MCharacterId'])
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
          act = get_skill(act['SkillRefId']) if act else ''
          action = act['Name'] if act else ''
      elif ch['HP'] == 0:
        action = '戦闘不能'
      elif 'BattleActions' in data:
        action = '行動不能'
      string += f"Action: {action}\n" if action else ''
      # string += '-----\n'
    string += "\n***** Enemies *****\n"
    for ch in data['BattleState']['Enemies']:
      name = get_enemy(ch['EID'])['Name']
      string += f"{name} (HP:{ch['CurrentHPPercent']}%)"
      if 'BattleActions' in data:
        action = next((act for act in data['BattleActions'] if act['ActorId'] == ch['ID']), None)
        if action:
          action = get_skill(action['SkillId'])
          string += f" Action: {action['Name']}"
      string += '\n'
      # string +='-----\n'
    string += "===============================\n"
    log_info(string)
  except Exception as err:
    log_error("Error occurred during loggin battle status:", handle_exception(err))

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

def process_battle(data):
  log_info("Battle started")
  log_battle_status(data)
  player.clear_cache()
  while not is_defeated(data) and data['BattleState']['BattleStatus'] != BATTLESTAT_VICTORY:
    actions = determine_actions(data)
    data = process_actions(actions)
    log_battle_status(data, actions)
    uwait(0.3)
    if Throttling:
      uwait(1)
  if is_defeated(data):
    process_defeat()
  else:
    res = process_victory()
    log_player_profile(res['UUser'])
    discord.update_player_profile(res['UUserPreferences']['Name'], res['UUser']['Level'])

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
    sid = int(input("Stage id: "))
  return sid

def process_rentalid_input():
  rid = 0
  valids = []
  pdat,odat = friend.get_rentals()
  for dat in pdat:
    valids.append(dat['UUserId'])
  for dat in odat:
    valids.append(dat['UUserId'])
  while rid not in valids:
    try:
      rid = int(input("Rental friend's id (0 for list availables): "))
    except Exception:
      rid = 0
    if not rid:
      friend.log_rentals(True)
  return rid

def main():
  global PartyId,StageId,BattleId,RentalUid
  PartyId = process_partyid_input()
  log_info("Party Id:", PartyId)
  StageId = process_stageid_input()
  RentalUid = process_rentalid_input()
  log_info("Rental Id:", RentalUid)
  discord.update_status(StageId)
  if RentalUid <= 0:
    RentalUid = 'null'
  cnt = 0
  while True:
    cnt += 1
    log_info(f"Running combat iteration#{cnt}")
    data = start_battle()
    if type(data) == int:
      if data == ERROR_NOSTAMINA:
        log_info("Recover Stamina")
        recover_stamina()
        continue
    else:
      BattleId = data['BattleId']
      process_battle(data)
    log_info("Battle Ended")
    uwait(1.5)
    if Throttling:
      uwait(1)

if __name__ == '__main__':
  try:
    main()
  except (SystemExit, KeyboardInterrupt):
    if LastErrorCode == 403:
      discord.update_status(0)
    exit()