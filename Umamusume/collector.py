import _G

def record_race_result(race_name, ranking):
  file = f"{_G.DataCollectDirectory}/{_G.CurrentUmaName}_racedata.csv"
  with open(file, 'a') as fp:
    ranking_str = str(ranking)+'着' if ranking > 0 else '着外'
    fp.write(f"{race_name},{ranking_str},")
    fp.write({','.join([str(n) for n in _G.CurrentAttributes])}+',')
    fp.write({'&'.join([str(n) for n in _G.CurrentOwnedSkills])})
    fp.write("\n")