import _G, game
import os, json
import fileinput
from copy import deepcopy
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
from _G import log_error,log_info

def load_header():
  if not os.path.exists(_G.DERPY_WAREHOUSE_HAEDER_PATH):
    return []
  ret = []
  with open(_G.DERPY_WAREHOUSE_HAEDER_PATH, 'r') as fp:
    for line in fp:
      ret.append(int(line))
  return ret

def save_header(dat, append=True):
  with open(_G.DERPY_WAREHOUSE_HAEDER_PATH, 'a' if append else 'w') as fp:
    if type(dat) == int:
      fp.write(f"{dat}\n")
    else:
      for n in dat:
        fp.write(f"{n}\n")

def load_database_incremental():
  if not os.path.exists(_G.DERPY_WAREHOUSE_CONTENT_PATH):
    yield {}
  else:
    for line in fileinput.input([_G.DERPY_WAREHOUSE_CONTENT_PATH]):
      yield line

def load_database():
  if not os.path.exists(_G.DERPY_WAREHOUSE_CONTENT_PATH):
    return []
  ret = []
  with open(_G.DERPY_WAREHOUSE_CONTENT_PATH, 'r') as fp:
    for line in fp:
      ret.append(json.loads(line))
  return ret

def save_database(dat, append=True):
  with open(_G.DERPY_WAREHOUSE_CONTENT_PATH, 'a' if append else 'w') as fp:
    if type(dat) == list:
      for obj in dat:
        fp.write(f"{json.dumps(obj)}\n")
    else:
      fp.write(f"{json.dumps(dat)}\n")

def get_race_replay(id):
  res = game.get_request(f"/api/Casino/Race/GetReplay/{id}")
  return json.loads(res['r'])

def get_past_racedata():
  res = game.get_request('/api/Casino/Race/GetPastSchedules')  
  return res['r']['list']

def interpret_race_data(race):
  obj = deepcopy(race)
  for i,char in enumerate(race['character']):
    obj['character'][i]['tactics'] = _G.DERPY_TACTIC_LIST.index(char['tactics'])
    obj['character'][i]['report'] = 0
    for ch in char['report']:
      obj['character'][i]['report'] += _G.DERPY_UMA_REPORT.index(ch)
    char['condition'] = char['condition'].replace("\n",'')
    obj['character'][i]['condition'] = next((i for i, cond in enumerate(_G.DERPY_CONDITION_LIST) if cond in char['condition']), 0)
    obj['character'][i]['speed'] = _G.DERPY_STAT_TABLE[char['speed']]
    obj['character'][i]['stamina'] = _G.DERPY_STAT_TABLE[char['stamina']]
    m_charbase = game.get_character_base(char['layerId'])
    obj['character'][i]['mCharacterBaseId'] = m_charbase['MCharacterBaseId']
    obj['character'][i]['country'] = _G.DERPY_CHARACTER_COUNTRY.index(m_charbase['MCharacterBase']['Country'])
  return obj

def interpret_race_replay(data):
  ret = []
  for character in data:
    obj = {
      'characterId': character['characterId'],
      'condition': character['condition'],
      'time': 0
    }
    for _,phase in character['actions'].items():
      for act in phase:
        obj['time'] += act['duration']

    ret.append(obj)
  return ret

def sweep_race_replays():
  exists = load_header()
  error = 0
  for i in range(0x7fffffff):
    if error > 3:
      log_info("Stopping sweeping race due to successive error (>3)")
      break
    if i in exists:
      print(f"Race#{i} already saved, skip")
      continue
    try:
      res = game.get_request(f"/api/Casino/Race/GetSchedule/{i}")
      race = res['r']['schedule']
    except (SystemExit,Exception) as err:
      log_error("Error sweeping race:", err)
      error += 1
      continue
    error = 0
    data = interpret_race_data(race)
    result = get_race_replay(data['id'])['data']
    data['result'] = interpret_race_replay(result)
    save_header(data['id'])
    save_database(data)
    print(f"Race#{race['id']} data saved")

def main():
  exists = load_header()
  races = get_past_racedata()
  for race in races:
    if race['id'] in exists:
      print(f"Race#{race['id']} already saved, skip")
      continue
    obj = interpret_race_data(race)
    result = get_race_replay(obj['id'])['data']
    obj['result'] = interpret_race_replay(result)
    save_header(obj['id'])
    save_database(obj)
    print(f"Race#{race['id']} data saved")

if __name__ == '__main__':
  game.init()
  main()
