from _G import *
from datetime import datetime
import json

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
    if t:
      t = jpt2localt(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S"))
    ret.append({
      'id': inf['Id'],
      'time': t
    })
  return ret

def complete_expeditions(ids):
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Expeditions/completeAll', 
    json.dumps({'uExpeditionIds': ids}), headers=Headers
  )
  if not is_response_ok(res):
    return False
  return True

def start_expeditions(ids):
  for id in ids:
    res = Session.post(f'https://mist-train-east4.azurewebsites.net/api/Expeditions/{id}/depart', headers=Headers)
    if not is_response_ok(res):
      return False
  return True

def main():
  expeds = get_expeditions()
  go_expeds = []
  ok_expeds = []
  for exped in expeds:
    id,ctime = exped['id'],exped['time']
    if not ctime:
      log_info(f"Expedition#{id} is ready for dispatch")
      go_expeds.append(id)
      continue
    log_info(f"Expedition#{id} complete time: {ctime.strftime('%Y-%m-%d@%H:%M:%S')}")
    if datetime.now() >= ctime:
      ok_expeds.append(id)
      go_expeds.append(id)
    uwait(0.5)
  if ok_expeds:
    complete_expeditions(ok_expeds)
    log_info("Expedition completed:", ok_expeds)
  else:
    log_info("No expedition completed")
  uwait(1)
  if go_expeds:
    start_expeditions(go_expeds)
    log_info("Expedition dispatched:", go_expeds)
  else:
    log_info("No ready expedition to be dispatched")


if __name__ == '__main__':
  main()