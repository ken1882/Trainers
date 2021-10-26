import _G
from _G import *
import game

JokerColor = '$'
PokerColors  = ['C', 'D', 'H', 'S']
PokerNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'J', 'Q', 'K']
PokerWeight  = {
  '0': 0,
  '1': 14,
  '2': 2,
  '3': 3,
  '4': 4,
  '5': 5,
  '6': 6,
  '7': 7,
  '8': 8,
  '9': 9,
  'X': 10,
  'J': 11,
  'Q': 12,
  'K': 13
}
BetRate  = 2
InitBets = 1900
FinalBets = 3900
MaxEarnPerDay = 5000000
MaxEarnPerRound = 1000000
BetGoal  = 6000000
LastRoundThreshold = 4900000
FlagLastRound = False
CurrentEarnedBets = 0

def format_curtime():
  return datetime.strftime(datetime.now(), '%H:%M:%S')

def log_info(*args):
  print(f"[{format_curtime()}] [INFO]:", *args)

def uwait(sec):
  sleep(sec + randint(0,8) / 10)

def start_game():
  log_info("Start game")
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Casino/Poker')
  print(res)

def game_over(submit_result):
  log_info("Game Over")
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Casino/Poker')
  rjs = res['r']
  print(rjs)
  won,have = rjs['WinCoinCount'],rjs['UserCoinCount']
  if submit_result:
    res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Casino/Poker/Result')
    print(res)
  log_info(f"Won bets {won}; Now have {have}")

def place_bet():
  log_info("Place Bet")
  bets = FinalBets if FlagLastRound else InitBets
  res = game.post_request(f'https://mist-train-east4.azurewebsites.net/api/Casino/Poker/Bet?type={BetRate}&betCoin={bets}')
  print(res)
  cards = res['r']
  log_info("Drew cards:", cards)
  return cards

def determine_card_keep(cards):
  colors  = []
  numbers = []
  for i in range(5):
    colors.append(cards[i*2])
    numbers.append(PokerNumbers.index(cards[i*2+1]))
  ret = []
  try:
    ret.append(colors.index(JokerColor))
  except Exception:
    pass
  # Straight, but noes not check royal ones
  num_ascend = sorted(numbers)
  st = num_ascend[0]
  _i = 0
  while _i < len(num_ascend):
    n = num_ascend[_i]
    if _i == 0:
      if n == 0:
        st = num_ascend[1]
        _i = 2
    elif n == st+1:
      st += 1
    else:
      st = -1
      break
    _i += 1

  if st == sorted(numbers)[-1]:
    return list(range(len(numbers))) # no card need to exchange
  # Pick 4 same color
  for c in PokerColors:
    if colors.count(c) + colors.count(JokerColor) >= 4:
      for i,c2 in enumerate(colors):
        if c == c2:
          ret.append(i)
      return ret
  # Pick 2 or more same number
  for i,n in enumerate(numbers):
    if numbers.count(n) >= 2:
      ret.append(i)
  if ret:
    return set(ret)
  return []

def exchange_cards(indicies):
  url = 'https://mist-train-east4.azurewebsites.net/api/Casino/Poker/ChangeHand?'
  params = []
  for i in indicies:
    params.append(f"changeIndexes={i}")
  res = game.post_request(url+'&'.join(params))
  print(res)
  return res['r']['RewardCoinCount']

def start_doubleup():
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Casino/Poker/DoubleUp/Start')
  print(res)
  return PokerWeight[res['r'][1]]

def continue_doubleup(ch):
  # 1=higher 2=lower
  log_info(f"Double up guessed {'higher' if ch == 1 else 'lower'}")
  res = game.post_request(f'https://mist-train-east4.azurewebsites.net/api/Casino/Poker/DoubleUp/Choose?choice={ch}')
  print(res)
  rjs = res['r']
  return (rjs['Result'] == 3, PokerWeight[rjs['DrawCard'][1]], rjs['RewardCoinCount'])

def process_doubleup():
  global CurrentEarnedBets,FlagLastRound
  cur = start_doubleup()
  bets = InitBets
  times = 0
  while bets < MaxEarnPerRound:
    times += 1
    if _G.Throttling:
      uwait(0.2)
    log_info(f"#{times}: card weight {cur}")
    param = 1
    if CurrentEarnedBets+bets >= BetGoal:
      log_info("Last goal achieved, end game")
      break
    elif not FlagLastRound and times >= 4 and cur in range(7,10):
      log_info("End doubleups due next round has high risk")
      break
    else:
      param = 1 if cur < 7 else 2
    failed,cur,bets = continue_doubleup(param)
    if failed:
      log_info(f"Double up failed, GG")
      return False # needn't submit result if lost
    elif not FlagLastRound and CurrentEarnedBets + bets*2 >= MaxEarnPerDay:
      log_info("End round for potential last shot")
      break
    else:
      log_info(f"Double up passed, current reward: {bets}")
  log_info("Double up ended, reward:", bets)
  return bets < MaxEarnPerRound # needn't submit result if reached max earn

def start():
  cards = place_bet()
  keeps = determine_card_keep(cards)
  log_info("Keep cards at index:", keeps)
  exchanges = list(range(5))
  for k in keeps:
    exchanges.remove(k)
  won = exchange_cards(exchanges)
  if _G.Throttling:
    uwait(0.5)
  if won == 0:
    log_info("GG")
    game_over(True)
  else:
    log_info("You win! Processed to double ups")
    submit = process_doubleup()
    game_over(submit)

def get_won_progress():
  res = game.get_request('https://mist-train-east4.azurewebsites.net/api/Casino/GetCasinoTop')
  print(res)
  return res['r']['TodayCasinoCoinStatus']['GetCoinValueToday']

def main():
  global CurrentEarnedBets,FlagLastRound
  start_game()
  CurrentEarnedBets = get_won_progress()
  while CurrentEarnedBets < MaxEarnPerDay: 
    log_info(f"Today's progress: {CurrentEarnedBets}")
    if CurrentEarnedBets >= LastRoundThreshold:
      FlagLastRound = True
      log_info("Last round")
    start()
    log_info(f"Today's progress: {CurrentEarnedBets}")
    uwait(0.5)
    if _G.Throttling:
      uwait(1)
    CurrentEarnedBets = get_won_progress() 

if __name__ == "__main__":
  game.init()
  main()