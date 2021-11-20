import _G
import game, player
from copy import deepcopy

BattlerPool = {}
BattlerStruct = {
  'actor': None,
  'cid': 0,
  'actions': {}
}
SkillStruct = {
  'id': 0,      # skill id
  'damage': 0,  # damage dealt
  'times': 0,   # times used
  'kills': 0,
}

# command id to skill id
CommandSkillMap = {}
CommandSkillActionTypes = [
  1,
]

def setup_battlers(data):
  '''
  This method should be called every start of battle
  '''
  global BattlerPool, CommandSkillMap
  CommandSkillMap = {}
  for ch in data['BattleState']['Characters']:
    cid = ch['CID']   # Ucharachter id
    sid = ch['ID']    # serial id
    actor = player.get_character_by_uid(ch['CID'])
    mchid = actor['MCharacterId']
    if mchid not in BattlerPool:
      bstruct = deepcopy(BattlerStruct)
      bstruct['actor'] = actor
      bstruct['cid'] = cid
      BattlerPool[mchid] = bstruct
    for skill in ch['Skills']:
      sid = skill['Id']
      rid = skill['SkillRefId']
      if sid in CommandSkillMap and rid != CommandSkillMap[sid]:
        _G.log_warning(f"Same command id mapped to different skill: {sid} => {rid} (was {CommandSkillMap[sid]})")
      CommandSkillMap[sid] = rid

def reset():
  global BattlerPool,CommandSkillMap
  BattlerPool = {}
  CommandSkillMap = {}

def analyze_action_result(commands, result):
  global BattlerPool,CommandSkillMap
  actions = result['BattleActions']
  skill_counted = set()
  for cmd in commands:
    sid = cmd['UnitSerialId']
    cid = cmd['CommandId']
    actor = player.get_character_by_uid(result['BattleState']['Characters'][sid-1]['CID'])
    sk_cid = CommandSkillMap.get(cid)
    command_skill = game.get_skill(sk_cid)
    for action in actions:
      if action['BattleActionType'] not in CommandSkillActionTypes:
        continue
      try:
        sk_aid = CommandSkillMap.get(action['SkillId'])
        if not sk_cid or not sk_aid:
          continue
        action_skill   = game.get_skill(sk_aid)
      except Exception as err:
        _G.log_error(err)
        continue
      # compare name in order to handle repeat skills
      if action['ActorId'] != sid or \
        command_skill['Name'] != action_skill['Name']:
        continue
      skill_id = command_skill['Id']
      mchid = actor['MCharacterId']
      if skill_id not in BattlerPool[mchid]['actions']:
        BattlerPool[mchid]['actions'][skill_id] = deepcopy(SkillStruct)
        BattlerPool[mchid]['actions'][skill_id]['id'] = skill_id
      BattlerPool[mchid]['actions'][skill_id]['damage'] += action['Value']
      if action['TargetCurrentHPPercent'] == 0:
        BattlerPool[mchid]['actions'][skill_id]['kills'] += 1
      # save counted to prevent recalculation of repeat skills
      hash_id = f"{mchid}_{skill_id}"
      if hash_id not in skill_counted:
        BattlerPool[mchid]['actions'][skill_id]['times']  += 1
        skill_counted.add(hash_id)

def format_analyze_result():
  string = '='*27+' Battle Record '+'='*27 + '\n'
  for _,battler in BattlerPool.items():
    string += game.get_character_name(battler['actor']['MCharacterId']) + ':\n'
    for skid,action in battler['actions'].items():
      skill = game.get_skill(skid)
      string += f"* {skill['Name']}\n"
      string += f"  - Total Damage: {action['damage']}\n"
      string += f"  -   Times used: {action['times']}\n"
      string += f"  -  Avg. Damage: {action['damage'] / action['times']}\n"
      string += f"  -        Kills: {action['kills']}\n"
    string += '-'*42+'\n'
  return string