from copy import deepcopy
from _G import *
import player

ChargeUseGold     = False
ChargeUseLesser   = True  # マナドリンクミニ, 自主練時間を1時間チャージできる。
ChargeUseMedium   = False # マナドリンク, 自主練時間を2時間チャージできる。
ChargeUseGreater  = False # マナドリンクメガ, 自主練時間を4時間チャージできる。

MoneyUsageThreshold = 10000000 # Will use gold if enabled and owned amount above this number
GoldCostPerUse = 15
GoldCharge     = 100

MaxCharge = 6000 * 12
KnapsackTable = {
  100: ChargeUseGold,
  6000: ChargeUseLesser,
  12000: ChargeUseMedium,
  24000: ChargeUseGreater,
}

EnergyItemTable = {
  70: 6000, 71: 12000, 72: 24000
}

def checkout():
  res = post_request('https://mist-train-east4.azurewebsites.net/api/Training/updateCheckPoint')
  return res['r']

def get_charge_items():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/Training/Items')
  return res['r']

# Uses greedy instead of DP due to items are divisible
def determine_charge_usage(cur, items):
  left = MaxCharge - cur
  ret = {w: 0 for w in items.keys()}
  for w,enabled in reversed(items.items()):
    if not enabled:
      continue
    n = min(items[w], left // w)
    ret[w] += n
    left -= w * n
  return ret

def charge_energy(goldcnt, payload):
  res = post_request(f"https://mist-train-east4.azurewebsites.net/api/Training/chargeEnergy?useMoneyCount={goldcnt}", payload)
  return res

def main():
  energy_left = checkout()['TrainingInfoEnergyLeft']
  log_info("Energy Left:", energy_left)
  uwait(0.3)
  items = {GoldCharge: 0}
  m_items = get_charge_items()
  for item in m_items:
    w = EnergyItemTable[item['MItemId']]
    if KnapsackTable[w]:
      items[w] = item['Stock']
    else:
      items[w] = 0
  if ChargeUseGold:
    gold = player.get_profile()['Money']
    log_info("Gold left:", gold, "; use gold to charge:", gold > MoneyUsageThreshold)
    if gold > MoneyUsageThreshold:
      items[GoldCharge] = gold // GoldCostPerUse
  uses = determine_charge_usage(energy_left, items)
  payload = {}
  for item in m_items:
    w = EnergyItemTable[item['MItemId']]
    if uses[w]:
      payload[item['Id']] = uses[w]
  log_info("Charge item uses:", uses)
  res = charge_energy(uses[GoldCharge], payload)
  log_info("Charge completed:", res['r'])

if __name__ == '__main__':
  main()