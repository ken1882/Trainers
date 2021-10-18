from _G import *
import player, game


MinimumKeepGold = 10000000

PurchaseItemTypes = [
  4,  # Consumables
  10  # Gears
]

def get_daily_shop():
  res = game.get_request('https://mist-train-east4.azurewebsites.net/api/Markets/DailyShop')
  return res['r']

def log_profile(pdat):
  string  = '\n===== Currency Owned =====\n'
  string += f"Gold: {pdat['Money']}\n"
  string += f"ミストジュエル (無償): {pdat['FreeGem']}\n"
  string += f"ミストジュエル (有償): {pdat['Gem']}\n"
  string += '==========================\n'
  log_info(string)

def determine_goods2buy(goods, gold, gem=0):
  buys = []
  for good in goods:
    if good['HasPurchased'] or good['Sold']:
      continue
    if good['ItemType'] not in PurchaseItemTypes:
      continue
    if good['RequiredGems'] or good['RequiredFreeGems']:
      continue
    if gold - (good['RequiredMoney'] or 0) < MinimumKeepGold:
      continue
    buys.append(good)
  return buys

def purchase_goods(goods):
  for good in goods:
    res = game.post_request(f"https://mist-train-east4.azurewebsites.net/api/Markets/DailyShopItems/{good['Id']}/purchase")
    if res:
      log_info(f"Purchased item#{good['Id']} ({get_readable_item_detail(good).split()[0]})")

def get_readable_item_detail(item):
  item = game.get_item(item)
  ret = ''
  if 'Name' in item:
    ret += item['Name'] + '\n'
    ret += "  {}\n".format(item['Description'].replace('\r\n','')) if 'Description' in item else ''
  elif 'MCharacterId' in item:
    ch = game.get_character_base(item['MCharacterId'])
    return f"ギヤ：{ch['Name']}{ch['MCharacterBase']['Name']}\n"
  else:
    ret = str(item) + '\n'
  return ret

def log_invoice(goods):
  string  = "\n===== Goods to buy =====\n"
  gdcost = 0
  fgcost = 0
  pgcost = 0
  for good in goods:
    good['RequiredMoney']    = good['RequiredMoney'] or 0
    good['RequiredFreeGems'] = good['RequiredFreeGems'] or 0
    good['RequiredGems']     = good['RequiredGems'] or 0
    gdcost += good['RequiredMoney']
    fgcost += good['RequiredFreeGems']
    pgcost += good['RequiredGems']
    string += get_readable_item_detail(good)
    string += f"ゴルト: {good['RequiredMoney']} ミストジュエル (無償): {good['RequiredFreeGems']} ミストジュエル (有償): {good['RequiredGems']}\n"
    string += '-----\n'
  string += "{}: {}\n".format('ゴルト', gdcost)
  string += "{}: {}\n".format('ミストジュエル (無償)', fgcost)
  string += "{}: {}\n".format('ミストジュエル (有償)', pgcost)
  string += '========================\n'
  log_info(string)

def main():
  pdat = player.get_profile()
  gold = pdat['Money']
  log_profile(pdat)
  shop  = get_daily_shop()
  goods = shop['Items']
  buys = determine_goods2buy(goods, gold)
  purchase_goods(buys)
  log_invoice(buys)

if __name__ == '__main__':
  game.init()
  main()