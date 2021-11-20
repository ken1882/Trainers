import sys

from requests import exceptions
import _G
from _G import *
import itertools
import pprint
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
import player
import friend
import discord
import Input, vktable
import game
import utils
from datetime import date, datetime, timedelta
from stage import StageAlias, StageData, RaidStages
from Input import input
import battle_analyzer

if _G.IS_WIN32:
  import win32con

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
  -1, # use event potions (id > 400) 
  0 # use most
]
RecoveryBatchAmount = 5 # How many items to use once

AutoSellItems = [
  #             type     Id  Maximum keep  Minimum keep
  (       ITYPE_GEAR,   106,         9900,         10), # Gear：[古の魔女の末裔]セイラム
  (      ITYPE_GEAR2,   106,         9900,         10), # Gear：[古の魔女の末裔]セイラム
]


ConsumableMaxKeepRatio = 0.995
ConsumableMinKeepRatio = 0.95
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

ReportDetail = {
  'start_t': datetime.now(),  # start time
  'end_t': 0,                 # end time (the time when report is presented)
  'paused_t': timedelta(),    # paused duration
  'times': 0,                 # how many times fighted
  'loots': {},                # loots
  'loot_n': {},               # times the loot dropped, used to calc drop rate
  'solds': {},                # loots sold
  'sells': {},                # stuff gained from selling loots
  'ap_recovery': {},          # ap recovery option used
  'stamina_cost': 0,          # stamina cost of current stage
  'win': 0,
  'lose': 0,
}

W_TYPE = 10 ** 6
W_QUANTITY = 10 ** 8

def hash_item_id(item, q=None):
  ret = item['ItemType'] * W_TYPE + item['ItemId']
  if q:
    ret += q * W_QUANTITY
  return ret

def dehash_item_id(id):
  if id < W_QUANTITY:
    return (id // W_TYPE, id % W_TYPE)
  return (id % W_QUANTITY // W_TYPE, id % W_TYPE, id // W_QUANTITY)

def start_battle(sid, pid, rid=0):
  log_info("Starting batlle")
  rid = rid if rid else 'null'
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/canstart/{sid}?uPartyId={pid}")
  if res['r']['FaildReason'] != ERROR_SUCCESS:
    return res['r']['FaildReason']
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/start/{sid}?uPartyId={pid}&rentalUUserId={rid}&isRaidHelper=null&uRaidId=null&raidParticipationMode=null")
  return res['r']

def start_raid(sid, pid, rid=0):
  log_info("Starting raid")
  rid = rid if rid else 'null'
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/canstartRaid/{sid}?uPartyId={pid}&isFriend=false&isHost=true&uRaidId=null")
  if res['r']['FaildReason'] != ERROR_SUCCESS:
    return res['r']['FaildReason']
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/start/{sid}?uPartyId={pid}&rentalUUserId={rid}&isRaidHelper=false&uRaidId=null&raidParticipationMode=0")
  return res['r']

def join_raid(sid, pid, rid=0, scope=3):
  log_info("Join raid")
  rid = rid if rid else 'null'
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/canstartRaid/{sid}?uPartyId={pid}&isFriend=false&isHost=true&uRaidId=null")
  if res['r']['FaildReason'] != ERROR_SUCCESS:
    return res['r']['FaildReason']
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/start/{sid}?uPartyId={pid}&rentalUUserId={rid}&isRaidHelper=false&uRaidId=null&raidParticipationMode=0")
  return res['r']

def process_actions(commands, verion):
  log_info("Process actions")
  res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Battle/attack/{BattleId}",
    {
      "Type":1,
      "IsSimulation": False,
      "Version": verion,
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
  result = res['r']
  battle_analyzer.analyze_action_result(commands, result)
  return result

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

def record_loot_sell(item, n):
  global ReportDetail
  hid = hash_item_id(item)
  if hid not in ReportDetail['solds']:
    ReportDetail['solds'][hid] = 0
  ReportDetail['solds'][hid] += n

def record_sell_earns(items):
  global ReportDetail
  for item in items:
    hid = hash_item_id(item)
    if hid not in ReportDetail['sells']:
      ReportDetail['sells'][hid] = 0
    ReportDetail['sells'][hid] += item['ItemQuantity']

def sell_surplus_loots(loots):
  global AutoSellItems
  for loot in loots:
    if loot['Sold']:
      continue
    maxn,minn = 0,0
    for it in AutoSellItems:
      if it[0] == loot['ItemType'] and it[1] == loot['ItemId']:
        maxn,minn = it[2],it[3]
        break
    else:
      if loot['ItemType'] == ITYPE_CONSUMABLE:
        maxn = game.get_consumable(loot['ItemId'])['PossesionLimit']
        minn = maxn * ConsumableMinKeepRatio
        maxn = maxn * ConsumableMaxKeepRatio
      else:
        continue
    sitem = player.get_item_stock(loot)
    if not sitem:
      continue
    curn = sitem['Stock']
    maxn = int(maxn)
    minn = int(minn)
    if curn <= maxn:
      continue
    res = player.sell_item(sitem, curn-minn)
    record_loot_sell(loot, curn-minn)
    record_sell_earns(res)
    log_info(f"Sold item {game.get_item_name(loot)}, amount={curn-minn}")

def process_victory():
  global LastBattleWon,ReportDetail
  log_info("Victory")
  LastBattleWon = True
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Battle/victory?isSimulation=false')
  ReportDetail['win'] += 1
  return res['r']

def process_defeat():
  global LastBattleWon,ReportDetail
  log_info("Defeat")
  LastBattleWon = False
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Battle/defeat?isSimulation=false')
  ReportDetail['lose'] += 1
  return res['r']

def record_ap_recovery(item, n):
  hid = hash_item_id(item)
  if hid not in ReportDetail['ap_recovery']:
    ReportDetail['ap_recovery'][hid] = 0
  ReportDetail['ap_recovery'][hid] += n

def recover_stamina():
  items = player.get_aprecovery_items()
  log_info("Recovery items:", pprint.pformat(items, indent=2), '-'*21, sep='\n')
  items = sorted(items, key=lambda i:i['Stock'])
  nidx  = None
  if RecoveryUsage == 1:
    for id in RecoveryUsageOrder:
      if id == 0:
        nidx = -1
        break
      elif id == -1:
        nidx = next((i for i,item in enumerate(items) if item["MItemId"] in range(400,9999)), -1)
      else:
        nidx = next((i for i,item in enumerate(items) if item["MItemId"] == id), -1)
      nidx = -1 if items[nidx]['Stock'] <= 0 else nidx
      if nidx >= 0:
        break
  elif RecoveryUsage == 0:
    nidx = -1
  if nidx == None:
    log_error("No enough potions!")
    return None
  item = items[nidx]
  num  = min(RecoveryBatchAmount, item['Stock'])
  ap1  = player.get_profile()['CurrentActionPoints']
  res  = player.use_aprecovery_item(item, num)
  ap2  = res['r']['CurrentStamina']
  item['ItemType'] = ITYPE_CONSUMABLE
  item['ItemId']   = item['MItemId']
  record_ap_recovery(item, num)
  if not res:
    log_error("Out of stamina!")
    return None
  log_info(f"Recovey {game.get_item_name(item)} used, stock left: {item['Stock']-num}")
  log_info("Current stamina:", ap2)
  return res

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
    log_error("Error occurred during logging battle status:", handle_exception(err))

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

def record_loots(loots):
  global ReportDetail
  for loot in loots:
    hid = hash_item_id(loot)
    hid2= hash_item_id(loot, loot['ItemQuantity'])
    if hid not in ReportDetail['loots']:
      ReportDetail['loots'][hid] = 0
    if hid2 not in ReportDetail['loot_n']:
      ReportDetail['loot_n'][hid2] = 0
    if not loot['Sold']:
      ReportDetail['loots'][hid] += loot['ItemQuantity']
    ReportDetail['loot_n'][hid2] += 1

def process_combat(data):
  global LastBattleWon,ReportDetail
  LastBattleWon = False
  ReportDetail['times'] += 1
  battle_analyzer.setup_battlers(data)
  log_info("Battle started")
  log_battle_status(data)
  battle_analyzer.setup_battlers(data)
  if not _G.PersistCharacterCache:
    player.clear_cache()
  while not is_defeated(data) and data['BattleState']['BattleStatus'] != BATTLESTAT_VICTORY:
    actions = determine_actions(data)
    data = process_actions(actions, data['Version'])
    log_battle_status(data, actions)
    uwait(0.3)
    if _G.Throttling:
      uwait(1)
  if is_defeated(data):
    process_defeat()
  else:
    res = process_victory()
    loots = res['QuestLoots']['Items']
    record_loots(loots)
    log_loots(loots)
    sell_surplus_loots(loots)
    log_player_profile(res['UUser'])
    discord.update_player_profile(res['UUserPreferences']['Name'], res['UUser']['Level'])
  return SIG_COMBAT_WON if LastBattleWon else SIG_COMBAT_LOST

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
  while not sid or not utils.isdigit(sid):
    inp = input("Stage id (enter 0 to see stored data): ")
    inp = inp.split()
    sid = inp[0]
    ser = inp[1] if len(inp) > 1 else ''
    if utils.isdigit(sid) and int(sid) == 0:
      string = format_padded_utfstring(('Id', 15, True), (' Alias', 10), ('Name', 50)) + '\n'
      for id,name in StageData.items():
        if id == 0:
          continue
        name = name[-1]
        alias = next((k for k,v in StageAlias.items() if v == id), '')
        if ser in alias or ser in name:
          string += format_padded_utfstring(
            (id, 15, True), (' '+alias, 10), (name, 50)
          ) + '\n'
      print(string, '-'*42)
      sid = ''
      continue
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
  global BattleId,LastErrorCode,LOG_STATUS
  LOG_STATUS = not _G.ARGV.less
  log_info("Stage/Party/Rental IDs:", sid, pid, rid)
  if sid in RaidStages:
    data = start_raid(sid, pid, rid)
  else:
    data = start_battle(sid, pid, rid)
  if type(data) == int:
    if data == ERROR_NOSTAMINA:
      log_info("Recover Stamina")
      recovered = recover_stamina()
      if not recovered:
        return SIG_COMBAT_STOP
      if sid in RaidStages:
        data = start_raid(sid, pid, rid)
      else:
        data = start_battle(sid, pid, rid)
      if data == ERROR_NOSTAMINA:
        log_error("Out of stamina, abort combat")
        return SIG_COMBAT_STOP
    elif data == ERROR_LIMIT_REACHED:
      log_info("Challenge limit reached")
      return SIG_COMBAT_STOP 
  if type(data) == dict and 'BattleId' in data:
    BattleId = data['BattleId']
    return process_combat(data)
  else:
    LastErrorCode = data
    raise RuntimeError(f"Unable to start battle (ERRNO={data})")

def reset_final_report():
  global ReportDetail
  ReportDetail = {
    'start_t': datetime.now(),
    'end_t': 0,
    'paused_t': timedelta(),
    'times': 0,
    'loots': {},
    'loot_n': {},
    'solds': {},
    'sells': {},
    'ap_recovery': {},
    'stamina_cost': 0,
    'win': 0,
    'lose': 0,
  }


def log_final_report():
  global ReportDetail,StageId
  print("Preparing report please wait...")
  ReportDetail['end_t'] = datetime.now()
  string  = f"\n{'='*30} Report {'='*30}\n"
  line_width = len(string.strip())
  try:
    string += f"{StageData[StageId][-1]}\n" if StageId in StageData else ''
    elapsed = ReportDetail['end_t'] - ReportDetail['start_t'] - ReportDetail['paused_t']
    string += "Start time:   " + ReportDetail['start_t'].strftime('%Y-%m-%d %H:%M:%S') + '\n'
    string += "End time:     " + ReportDetail['end_t'].strftime('%Y-%m-%d %H:%M:%S') + '\n'
    string += "Time elapsed: " + format_timedelta(elapsed) + f" ({format_timedelta(ReportDetail['paused_t'])} paused)" + '\n'
    string += f"Combat status: {ReportDetail['times']} fights, Win/Lose={ReportDetail['win']}/{ReportDetail['lose']} ({int(ReportDetail['win'] / ReportDetail['times'] * 100)}%)\n"
    string += f"Average time spent per fight: {format_timedelta(elapsed / ReportDetail['times'])}\n"
    string += f"Stamina used: {ReportDetail['stamina_cost'] * ReportDetail['times']}\n"
    keys = ['ap_recovery', 'loots', 'solds', 'sells', 'loot_n']
    subtitles = ("Recovery items used", "Loots Gained", "Loots Sold", "Sell Earnings", "Loots Drop Rate")
    for idx,key in enumerate(keys):
      subtitle = subtitles[idx]
      spacing = (line_width - 2 - len(subtitle)) // 2
      string += f"\n{'-'*spacing} {subtitle} {'-'*spacing}\n"
      for hid,n in ReportDetail[key].items():
        if hid == 0:
          continue
        info = dehash_item_id(hid)
        if len(info) == 2:
          itype,iid = info
        else:
          itype,iid,qn = info
        item_info = {'ItemType': itype, 'ItemId': iid}
        name = game.get_item_name(item_info)
        if key != 'loot_n':
          string += '{:>10}x {}'.format(n, name)
          try:
            stock = player.get_item_stock(item_info, True)
            string += f" (Now have x{stock})"
          except (Exception, SystemExit, InterruptedError) as err:
            log_error("Unable to get item stock:", err, '\nSkip stock logging.')
          string += '\n'
        else:
          string += format_padded_utfstring((f"{qn}x{name}", 40, True))
          string += ": {:.5f}%".format(n / ReportDetail['win'] * 100)
          string += f" dropped {n} time(s)\n"
    # end report category listings
  except Exception as err:
    log_error(f"An error occured while logging final report: {err}")
    handle_exception(err)
  string += f"\n{'='*68}\n"
  if _G.ARGV.output:
    try:
      with open(_G.ARGV.output, 'a') as fp:
        fp.write(string)
    except Exception as err:
      log_error(f"An error occured while writing result file: {err}")
      handle_exception(err)
  print(string)
  print(battle_analyzer.format_analyze_result())

def update_input():
  global FlagRequestReEnter
  if not utils.is_focused():
    return
  Input.update()
  if Input.is_trigger(vktable.VK_F7):
    _G.FlagPaused ^= True
    print("Worker", 'paused' if _G.FlagPaused else 'unpaused')
  elif Input.is_trigger(vktable.VK_F8):
    _G.FlagRunning = False
    _G.FlagPaused  = False
  elif Input.is_trigger(vktable.VK_F5):
    FlagRequestReEnter = True

def process_prepare_inputs():
  global ReportDetail
  sid = process_stageid_input()
  pid = process_partyid_input()
  log_info("Party Id:", pid)
  rid = process_rentalid_input()
  log_info("Rental Id:", 'Round-Robin' if rid == -1 else rid)
  if rid != -1 and rid <= 0:
    rid = 'null'
  ReportDetail['stamina_cost'] = game.get_quest(sid)['ActionPointsCost']
  return (pid, sid, rid)

def main():
  global PartyId,StageId,RentalUid,AvailableFriendRentals,RentalCycle
  global FlagRequestReEnter,ReportDetail
  log_info("Program initialized")
  reset_final_report()
  battle_analyzer.reset()
  PartyId,StageId,RentalUid = process_prepare_inputs()
  discord.update_status(StageId)
  cnt = 0
  while _G.FlagRunning:
    if _G.FlagPaused:
      pt_s = datetime.now()
      while _G.FlagPaused:
        update_input()
        if Input.is_trigger(vktable.VK_F6):
          log_final_report()
        if not _G.FlagPaused:
          ReportDetail['paused_t'] += datetime.now() - pt_s
        wait(0.1)
      continue
    if FlagRequestReEnter:
      log_final_report()
      reset_final_report()
      battle_analyzer.reset()
      PartyId,StageId,RentalUid = process_prepare_inputs()
      discord.update_status(StageId)
      FlagRequestReEnter = False
      cnt = 0
      continue
    cnt += 1
    log_info(f"Running combat iteration#{cnt}")
    rid = RentalUid
    if rid == -1:
      rid = next(RentalCycle)
    signal = start_battle_process(StageId, PartyId, rid)
    log_info("Battle Ended")
    if signal == SIG_COMBAT_STOP:
      break
    uwait(1)
    if _G.Throttling:
      uwait(1)
    update_input()
  log_final_report()

if __name__ == '__main__':
  try:
    game.init()
    Input.init()
    main()
    _G.FlagRunning = False
  except (Exception, SystemExit, KeyboardInterrupt) as err:
    log_final_report()
    if LastErrorCode == 403:
      discord.update_status(0)
    handle_exception(err)
    exit()
  finally:
    if _G.IS_LINUX:
      Input.restore_terminal_settings()