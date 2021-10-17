from _G import *
import game

def get_friends():
  res = game.get_request('https://mist-train-east4.azurewebsites.net/api/Friends')
  return res['r']

def get_rentals():
  res = game.get_request('https://mist-train-east4.azurewebsites.net/api/Friends/Rental')
  return [res['r']['FriendUsers'], res['r']['OtherUsers']]

def send_request(duid):
  res = game.get_request(f"https://mist-train-east4.azurewebsites.net/api/Friends/Search/{duid}")
  res = game.post_request("https://mist-train-east4.azurewebsites.net/api/Friends/SendRequests", [res['r']['UUserId']])
  return res


def log_rentals(ls_others=False):
  fdat,odat      = get_rentals()
  width_name  = 20
  width_sname = 40
  width_id    = 12
  width_fpts  = 15
  string  = '\n'+ '='*30 + ' Rentals ' + '='*30 + '\n'
  string += 'Friends:\n'
  string += format_padded_utfstring(
    ('Name', width_name, True), ('Skill Name', width_sname, True),('Id', width_id, True), ('Friend Points', width_fpts, True)
  ) + '\n'
  for dat in fdat:
    if not dat['MFieldSkillId']:
      continue
    fsk = game.get_fskill(dat['MFieldSkillId'])
    string += format_padded_utfstring(
      (dat['Name'], 20, True),
      (f"{fsk['Name']} (LV.{dat['FieldSkillLevel']}/{fsk['MFieldSkillRarity']['LevelLimit']})", width_sname, True),
      (dat['UUserId'], width_id, True),
      (dat['FriendMeterPoint'], width_fpts, True)
    ) + '\n'
  if not ls_others:
    string += '='*69 + '\n'
    log_info(string)
    return
  string += "\nOthers:\n"
  string += format_padded_utfstring(
    ('Name', width_name, True), ('Skill Name', width_sname, True),('Id', width_id, True)
  ) + '\n'
  for dat in odat:
    if not dat['MFieldSkillId']:
      continue
    fsk = game.get_fskill(dat['MFieldSkillId'])
    string += format_padded_utfstring(
      (dat['Name'], 20, True),
      (f"{fsk['Name']} (LV.{dat['FieldSkillLevel']}/{fsk['MFieldSkillRarity']['LevelLimit']})", width_sname, True),
      (dat['UUserId'], width_id, True)
    ) + '\n'
  string += '='*69 + '\n'
  log_info(string)