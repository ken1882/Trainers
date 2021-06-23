import _G
import os

StatusName = ('絕不調','不調','普通','好調','絕好調')

def init_race_file(filename):
  with open(filename, 'w', encoding='utf8') as fp:
    fp.write("Race,Ranking,retries,Status,Attributes,Skill Points Spent,Skills\n")

def record_race_result(race_name, ranking, retries):
  file = f"{_G.DataCollectDirectory}/{_G.CurrentUmaName}_racedata.csv"
  if not os.path.exists(file):
    init_race_file(file)
  with open(file, 'a', encoding='utf8') as fp:
    ranking_str = str(ranking)+'着' if ranking > 0 else '着外'
    fp.write(f"{race_name},{ranking_str},{retries},{StatusName[_G.CurrentStatus]},")
    fp.write({';'.join([str(n) for n in _G.CurrentAttributes[:5]])}+',')
    fp.write({'&'.join([str(f"({sk[0]},{sk[1]})") for sk in _G.CurrentOwnedSkills])})
    fp.write("\n")