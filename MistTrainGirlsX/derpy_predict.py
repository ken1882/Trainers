import game, _G
import matplotlib
matplotlib.use('Agg')
from matplotlib import get_backend
import matplotlib.pyplot as plt
import pickle
import numpy as np
from derpy_datamanager import interpret_race_data
from pprint import pprint

def get_upcoming_race():
  game.init()
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Casino/Race/GetPaddock')
  return res['r']['data']

def predict_race(race):
  x_train = []
  data = race['schedule']
  n_uma = len(race['character'])
  for ch in race['character']:
    features = [
      data['direction'],
      data['grade'],
      n_uma,
      ch['range'],
      abs(data['type'] - ch['forte']),
      abs(data['weather'] - ch['weather']),
      ch['tactics'],
      ch['report'],
      ch['condition'],
      ch['speed'],
      ch['stamina'],
      ch['number'],
    ]
    x_train.append(features)
  
  with open(_G.DERPY_MODEL_NAME, 'rb') as fp:
    clsier = pickle.load(fp)

  result = clsier.predict(x_train)
  return result

def format_derpy_data(data, predict):
  string = '='*69 + '\n'
  string += f"{data['schedule']['name']}\n"
  string += f"{_G.DERPY_RANGE_LIST[data['schedule']['range']]} {_G.DERPY_GROUND_TYPE[data['schedule']['type']]} "
  string += f"{_G.DERPY_DIRECTION_TYPE[data['schedule']['direction']]} {_G.DERPY_WEATHER_TYPE[data['schedule']['weather']]}\n"
  string += '-' * 42 + '\n'
  SCORE_WIDTH = 8
  PRED_WIDTH  = 8
  NUM_WIDTH   = 5
  NAME_WIDTH  = 40
  REPORT_WIDTH = 5
  FORTE_WIDTH = 7
  TACTIC_WIDTH = 6
  SPEED_WIDTH = 5
  STAMINA_WIDTH = 5
  WEATHER_WIDTH = 5
  CONDITION_WIDTH = 5
  POPULARITY_WIDTH = 5
  string += _G.format_padded_utfstring(
    ('騎番', NUM_WIDTH, 1), ('名前', NAME_WIDTH, 1), 
    ('期待値', SCORE_WIDTH, 1), ('予想着', PRED_WIDTH, 1),
    ('予想', REPORT_WIDTH, 1),
    ('作戦', TACTIC_WIDTH, 1), ('得意', FORTE_WIDTH, 1), 
    ('スピ', SPEED_WIDTH, 1), ('スタ', STAMINA_WIDTH, 1),
    ('状態', CONDITION_WIDTH, 1), ('天気', WEATHER_WIDTH, 1),
    ('人気', POPULARITY_WIDTH, 1),
  ) + '\n'
  order = sorted(predict, reverse=True)
  for i,ch in enumerate(data['character']):
    spd_chr = next((c for c,n in _G.DERPY_STAT_TABLE.items() if n == ch['speed']), 'G')
    sta_chr = next((c for c,n in _G.DERPY_STAT_TABLE.items() if n == ch['stamina']), 'G')
    string += _G.format_padded_utfstring(
      (ch['number'], NUM_WIDTH, 1), (game.get_character_name(ch['layerId']), NAME_WIDTH, 1),
      (int(predict[i]), SCORE_WIDTH, 1), (next((n+1 for n,v in enumerate(order) if v == predict[i]), 0), PRED_WIDTH, 1),
      (ch['report'], REPORT_WIDTH, 1),
      (_G.DERPY_TACTIC_LIST[ch['tactics']][:2], TACTIC_WIDTH, 1), (_G.DERPY_GROUND_TYPE[ch['forte']], FORTE_WIDTH, 1), 
      (spd_chr, SPEED_WIDTH, 1), (sta_chr, STAMINA_WIDTH, 1),
      (ch['condition'], CONDITION_WIDTH, 1), (_G.DERPY_WEATHER_TYPE[ch['weather']], WEATHER_WIDTH, 1),
      (ch['popularity'], POPULARITY_WIDTH, 1),
    ) + '\n'
  return string

def main():
  race = get_upcoming_race()
  race = interpret_race_data(race)
  predict = predict_race(race)
  print(predict)
  print(format_derpy_data(race, predict))
  

if __name__ == '__main__':
  main()