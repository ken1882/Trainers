from _G import *

def get_profile():
  res  = get_request('https://mist-train-east4.azurewebsites.net/api/Users/Me')['r']
  res2 = get_request('https://mist-train-east4.azurewebsites.net/api/Users/MyPreferences')['r']
  ret = {**res, **res2}
  return ret

def get_characters():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/UCharacters')
  return res['r']

def get_parties(upid):
  res = get_request(f"https://mist-train-east4.azurewebsites.net/api/UParties/GetUPartiesFromUPartyId/{upid}")
  return res['r']