from _G import *

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
Throttling = True
LastRoundThreshold = 4900000
FlagLastRound = False
CurrentEarnedBets = 0

def format_curtime():
  return datetime.strftime(datetime.now(), '%H:%M:%S')

def log_info(*args):
  print(f"[{format_curtime()}] [INFO]:", *args)

def uwait(sec):
  sleep(sec + randint(0,8) / 10)

headers = {
  'Authorization': sys.argv[1]
}
Session = requests.Session()
Session.headers = headers

def start_game():
  log_info("Start game")
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Casino/Poker')
  print(res, res.json())

def game_over():
  log_info("Game Over")
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Casino/Poker')
  rjs = res.json()['r']
  print(res, rjs)
  won,have = rjs['WinCoinCount'],rjs['UserCoinCount']
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Casino/Poker/Result')
  print(res, res.json())
  log_info(f"Won bets {won}; Now have {have+won}")

def place_bet():
  log_info("Place Bet")
  bets = FinalBets if FlagLastRound else InitBets
  res = Session.post(f'https://mist-train-east4.azurewebsites.net/api/Casino/Poker/Bet?type={BetRate}&betCoin={bets}')
  print(res, res.json())
  cards = res.json()['r']
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
  # Straight, skip joker check due to the low chance
  st = sorted(numbers)[0]
  for i,n in enumerate(sorted(numbers)):
    if i == 0:
      continue
    if n == st+1:
      st += 1
    else:
      st = -1
      break
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
  res = Session.post(url+'&'.join(params))
  print(res, res.json())
  return res.json()['r']['RewardCoinCount']

def start_doubleup():
  res = Session.post('https://mist-train-east4.azurewebsites.net/api/Casino/Poker/DoubleUp/Start')
  print(res, res.json())
  return PokerWeight[res.json()['r'][1]]

def continue_doubleup(ch):
  # 1=higher 2=lower
  log_info(f"Double up guessed {'higher' if ch == 1 else 'lower'}")
  res = Session.post(f'https://mist-train-east4.azurewebsites.net/api/Casino/Poker/DoubleUp/Choose?choice={ch}')
  print(res, res.json())
  rjs = res.json()['r']
  return (rjs['Result'] == 3, PokerWeight[rjs['DrawCard'][1]], rjs['RewardCoinCount'])

def main():
  global CurrentEarnedBets,FlagLastRound
  cards = place_bet()
  keeps = determine_card_keep(cards)
  log_info("Keep cards at index:", keeps)
  exchanges = list(range(5))
  for k in keeps:
    exchanges.remove(k)
  won = exchange_cards(exchanges)
  if Throttling:
    uwait(0.5)
  if won == 0:
    log_info("GG")
    game_over()
  else:
    log_info("You win! Processed to double ups")
    cur = start_doubleup()
    bets = InitBets
    times = 0
    while bets < MaxEarnPerRound:
      times += 1
      if Throttling:
        uwait(0.2)
      log_info(f"#{times}: card weight {cur}")
      param = 1
      if not FlagLastRound and times >= 4 and cur in range(7,10):
        log_info("End doubleups")
        break
      else:
        param = 1 if cur < 7 else 2
      failed,cur,bets = continue_doubleup(param)
      if failed:
        log_info(f"Double up failed, GG")
        break
      elif CurrentEarnedBets + bets >= MaxEarnPerDay:
        log_info("End round to process to last shot")
        break
      else:
        log_info(f"Double up passed, current reward: {bets}")
    log_info("Double up ended")
    game_over()

def get_won_progress():
  res = Session.get('https://mist-train-east4.azurewebsites.net/api/Casino/GetCasinoTop')
  print(res, res.json())
  return res.json()['r']['TodayCasinoCoinStatus']['GetCoinValueToday']

def start():
  global CurrentEarnedBets,FlagLastRound
  start_game()
  CurrentEarnedBets = get_won_progress()
  while CurrentEarnedBets < BetGoal:
    CurrentEarnedBets = get_won_progress()  
    log_info(f"Today's progress: {CurrentEarnedBets}")
    if CurrentEarnedBets >= LastRoundThreshold:
      FlagLastRound = True
      log_info("Last round")
    main()
    sleep(0.5)
    if Throttling:
      sleep(1)

start()