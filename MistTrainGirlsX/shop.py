from glob import glob
from _G import *
import player, game
import mtg_parser


MinimumKeepGold = 10000000

PurchaseItemTypes = [
  4,  # Consumables
  10  # Gears
]

TradeVoteGood = None

def get_daily_shop():
  res = game.get_request('/api/Markets/DailyShop')
  return res['r']

def get_event_shops():
  res = game.get_request('/api/TradeShops')
  shops = [mtg_parser.parse_trade_shop(o) for o in res]
  return [s for s in shops if s['TradeShopType'] == SHOP_TYPE_EVENT]

def get_tshop_goods(id):
  res = game.get_request(f"/api/TradeShops/{id}/lineup")
  return mtg_parser.parse_trade_shop_goods(res)['Rewards']

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
    res = game.post_request(f"/api/Markets/DailyShopItems/{good['Id']}/purchase")
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

def trade_item(good_id, amount):
  res = game.post_request(f"/api/TradeRewards/{good_id}/trade/{amount}")
  return res

def trade_all_event_potions():
  stores = get_event_shops()
  for st in stores:
    currency = {it['MItemId']: it['Stock'] for it in st['CurrencyStocks']}
    goods = get_tshop_goods(st['Id'])
    goods = sorted(goods, key=lambda it:(it['Limit'] or 0)*it['RequiredMItemNum'])
    for good in goods:
      name = game.get_item_name(good)
      if 'ポーション' in name:
        price   = good['RequiredMItemNum']
        balance = currency[good['RequiredMItemId']]
        if price < 200:
          continue # probaby costs limited currency
        if balance < price:
          log_info(f"Insufficient balance to buy {name}, costs {price} but only have {balance}")
          continue
        n = balance // price
        trade_item(good['Id'], n)
        currency[good['RequiredMItemId']] -= price * n
        log_info(f"Traded potion {name} x{n}, now have {player.get_item_stock(good, True)}; currency left: {currency}")
  
def trade_all_event_goods():
  stores = get_event_shops()
  for st in stores:
    currency = {it['MItemId']: it['Stock'] for it in st['CurrencyStocks']}
    goods = get_tshop_goods(st['Id'])
    goods = sorted(goods, key=lambda it:(it['Limit'] or 0)*it['RequiredMItemNum'])
    log_info(f"Trade shop#{st['Id']} currency owned:", currency, sep='\n')
    for good in reversed(goods):
      price = good['RequiredMItemNum']
      balance = currency[good['RequiredMItemId']]
      name = game.get_item_name(good)
      if good['Limit']:
        stock = good['Limit'] - good['TradedCount']
        if stock == 0:
          log_info(f"{name} is out of stock!")
          continue
      n = 0
      if price > balance:
        log_info(f"Cannot afford to buy {name}, requires {price} but only have {balance}; Exit shop")
        break
      if not good['Limit']: # Good with infinite trade count, should be bought at last
        if good['ItemType'] == ITYPE_GOLD:
          continue
        n = balance // price
        trade_item(good['Id'], n)
      else: # Limited goods, should be traded first
        n = min(stock, balance // price)
        trade_item(good['Id'], n)
      currency[good['RequiredMItemId']] -= price * n
      log_info(f"Traded good {name} x{n}, currency left: {currency}")

def buy_votes():
  global TradeVoteGood
  if not TradeVoteGood:
    for s in get_event_shops():
      for g in get_tshop_goods(s['Id']):
        if '投票券' not in game.get_item_name(g):
          continue
        log_info("Vote item set:", game.get_item_name(g))
        TradeVoteGood = g
        break
      if TradeVoteGood:
        break
  currency = player.get_consumable_stock(TradeVoteGood['RequiredMItemId'],category=ICATE_TRADE)['Stock']
  cost = TradeVoteGood['RequiredMItemNum']
  if currency < cost * 1000:
    return 0
  n = currency // cost
  res = trade_item(TradeVoteGood['Id'], n)
  log_info('Purchased votes:', n, 'res:', res)
  vid = TradeVoteGood['ItemId']
  player.VoteItemId = vid
  player.ConsumableInventory[vid] = player.get_consumable_stock(vid, category=ICATE_VOTE_TICKET)['Stock']
  return n

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