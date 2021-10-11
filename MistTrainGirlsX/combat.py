from time import thread_time
from _G import *
import pprint
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
import json
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
  2,
]
RecoveryUsage = 424 # 0=Use most, others=Use with that item id if exists
RecoveryBatchAmount = 5 # How many items to use once
Throttling = False
UnmovableEffects = [22,23]

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}

def start_battle():
  res = Session.post(f"https://mist-train-east4.azurewebsites.net/api/Battle/canstart/{StageId}?uPartyId={PartyId}")
  if not is_response_ok(res):
    exit()
  rsj = res.json()
  if rsj['r']['FaildReason'] != ERROR_SUCCESS:
    return rsj['r']['FaildReason']
  res = Session.post(f"https://mist-train-east4.azurewebsites.net/api/Battle/start/{StageId}?uPartyId={PartyId}&rentalUUserId={RentalUid}&isRaidHelper=null&uRaidId=null&raidParticipationMode=null")
  if not is_response_ok(res):
    exit()
  return res.json()['r']

def process_actions(commands):
  log_info("Process actions")
  res = Session.post(f"https://mist-train-east4.azurewebsites.net/api/Battle/attack/{BattleId}",
    json.dumps({
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
    }),
    headers=Headers
  )
  if not is_response_ok(res):
    exit()
  return res.json()['r']

def get_movable_characters(characters):
  ret = []
  for ch in characters:
    if ch["HP"] <= 0:
      continue
    if any([ stat["SkillEffectType"] in UnmovableEffects for stat in ch["Auras"] ]):
      continue
    ret.append(ch)
  return ret

def determine_skill(character):
  sp = character['SP']
  skills = []
  for sk in character['Skills']:
    if not sk['IsCommandSkill']:
      continue
    if (sk['Id'] <= 0 or sk['SP'] <= 0) and sk['SkillType'] != 5:
      continue
    skills.append(sk)
  skills = sorted(skills, key=lambda s:s['SP'])
  if BattleStyle[character['ID']] == 1 and sp >= skills[-1]['SP']:
    return skills[-1]['Id']
  elif BattleStyle[character['ID']] == 2:
    ret = 0
    for sk in skills:
      if sp >= sk['SP']:
        ret = sk['Id']
    return ret
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
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Battle/victory?isSimulation=false')
  if not is_response_ok(res):
    exit()
  return res.json()['r']

def recover_stamina():
  res = Session.get('https://mist-train-east4.azurewebsites.net/api/UItems/ApRecoveryItems')
  if not is_response_ok(res):
    exit()
  items = res.json()['r']
  log_info("Recovery items:", pprint.pformat(items, indent=2), '-'*21, sep='\n')
  items = sorted(items, key=lambda i:i['Stock'])
  nidx  = -1
  if RecoveryUsage != 0:
    nidx = next((i for i,item in enumerate(items) if item["MItemId"] == RecoveryUsage), -1)
  nid = items[nidx]['MItemId']
  num = min(RecoveryBatchAmount, items[nidx]['Stock'])
  res = Session.post(f"https://mist-train-east4.azurewebsites.net/api/Users/recoverStamina/{nid}/{num}")
  log_info(f"Recovey item@{nid} used, stock left: {items[nidx]['Stock']-num}")
  if not is_response_ok(res):
    exit()
  log_info("Current stamina:", res.json()['r']['CurrentStamina'])

def log_battle_status(data):
  string  = '\n====== Status ======\n'
  string += f"Wave#{data['BattleState']['WaveNumber']} Turn#{data['BattleState']['TurnNumber']}\n"
  string += "----- Players -----\n"
  for ch in data['BattleState']['Characters']:
    string += f"ID#{ch['ID']} HP:{ch['HP']} SP:{ch['SP']} OP:{ch['OP']}\n"
  string += "----- Enemies -----\n"
  for ch in data['BattleState']['Enemies']:
    string += f"ID#{ch['ID']} HP:{ch['CurrentHPPercent']}%\n"
  string += "====================\n"
  log_info(string)

def log_player_profile(data):
  string  = '\n===== Player Info =====\n'
  string += f"Level: {data['Level']}\n"
  string += f"Exp: {data['TotalExperience']}\n"
  string += f"Gold: {data['Money']}\n"
  string += f"Stamina: {data['CurrentActionPoints']} / {data['MaxActionPoints']}\n"
  string += "=======================\n"
  log_info(string)

def process_battle(data):
  log_info("Battle started")
  log_battle_status(data)
  while data['BattleState']['BattleStatus'] != BATTLESTAT_VICTORY:
    actions = determine_actions(data)
    log_info("Actions:")
    pp.pprint(actions)
    data = process_actions(actions)
    log_battle_status(data)
    uwait(0.3)
    if Throttling:
      uwait(1)
  res = process_victory()
  log_player_profile(res['UUser'])
  discord.update_player_profile(res['UUserPreferences']['Name'], res['UUser']['Level'])

def main():
  global PartyId,StageId,BattleId,RentalUid
  PartyId = int(input("Party id: "))
  StageId = int(input("Stage id: "))
  RentalUid = int(input("Rental friend's id (0 for none): "))
  if RentalUid <= 0:
    RentalUid = 'null'
  while True:
    data = start_battle()
    if type(data) == int:
      if data == ERROR_NOSTAMINA:
        log_info("Recover Stamina")
        recover_stamina()
    else:
      BattleId = data['BattleId']
      process_battle(data)
    log_info("Battle Ended")
    uwait(1.5)
    if Throttling:
      uwait(1)

if __name__ == '__main__':
  main()