from _G import *
from datetime import date, datetime

Headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br'
}

def get_expeditions():
  res = Session.get('https://mist-train-east4.azurewebsites.net/api/Expeditions')
  if not is_response_ok(res):
    return []
  rsj = res.json()
  ret = []
  for inf in rsj['r']:
    t = inf['CompletedAt']
    ret.append({
      'id': inf['Id'],
      'time': datetime.strptime(t, "%Y-%m-%dT%H:%M:%S") if t else None
    })
  return ret

def complete_expeditions(ids):
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Expeditions/completeAll', {
    'uExpeditionIds': ids
  })
  if not is_response_ok(res):
    return False
  return True

def start_expeditions(ids):
  for id in ids:
    res = Session.post(f'https://mist-train-east4.azurewebsites.net/api/Expeditions/{id}/depart', headers=Headers)
    if not is_response_ok(res):
      return False
  return True