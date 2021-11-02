import game, _G
import matplotlib
matplotlib.use('Agg')
from matplotlib import get_backend
import matplotlib.pyplot as plt
import pickle
import numpy as np
from derpy_datamanager import interpret_race_data
from pprint import pprint


ESTIMATORS = [f"{_G.DCTmpFolder}/{_G.make_model_name(d)}" for d in _G.DERPY_TRAINING_LIST]

def get_upcoming_race():
  game.init()
  res = game.post_request('https://mist-train-east4.azurewebsites.net/api/Casino/Race/GetPaddock')
  return res['r']['data']

def predict_race(estimator, race):
  x_train = []
  data = race['schedule'] if 'schedule' in race else race
  data['result'] = race['character'] # used for feature extract function
  for ch in race['character']:
    if 'feats_all' in estimator:
      features = _G.extract_derpy_features(data, ch, 'all')
    elif 'feats_noreport' in estimator:
      features = _G.extract_derpy_features(data, ch, 'noreport')
    x_train.append(features)

  with open(estimator, 'rb') as fp:
    clsier = pickle.load(fp)

  result = clsier.predict(x_train)
  return result

def format_derpy_data(data, predict, score_proc):
  race = data['schedule'] if 'schedule' in data else data
  string = '='*69 + '\n'
  string += f"{race['name']}\n"
  string += f"{_G.DERPY_RANGE_LIST[race['range']]} {_G.DERPY_GROUND_TYPE[race['type']]} "
  string += f"{_G.DERPY_DIRECTION_TYPE[race['direction']]} {_G.DERPY_WEATHER_TYPE[race['weather']]}\n"
  string += '-' * 42 + '\n'
  SCORE_WIDTH = 8
  PRED_WIDTH  = 8
  NUM_WIDTH   = 5
  WAKU_WIDTH  = 5
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
    ('騎番', NUM_WIDTH, 1), ('枠番', WAKU_WIDTH, 1),
    ('名前', NAME_WIDTH, 1), 
    ('期待値', SCORE_WIDTH, 1), ('予想着', PRED_WIDTH, 1),
    ('予想', REPORT_WIDTH, 1),
    ('作戦', TACTIC_WIDTH, 1), ('得意', FORTE_WIDTH, 1), 
    ('スピ', SPEED_WIDTH, 1), ('スタ', STAMINA_WIDTH, 1),
    ('状態', CONDITION_WIDTH, 1), ('天気', WEATHER_WIDTH, 1),
    ('人気', POPULARITY_WIDTH, 1),
  ) + '\n'
  for i,ch in enumerate(data['character']):
    spd_chr = next((c for c,n in _G.DERPY_STAT_TABLE.items() if n == ch['speed']), 'G')
    sta_chr = next((c for c,n in _G.DERPY_STAT_TABLE.items() if n == ch['stamina']), 'G')
    score, rank = score_proc(ch, predict)
    string += _G.format_padded_utfstring(
      (ch['number'], NUM_WIDTH, 1), (ch['waku'], WAKU_WIDTH, 1),
      (game.get_character_name(ch['layerId']), NAME_WIDTH, 1),
      (score, SCORE_WIDTH, 1), (rank, PRED_WIDTH, 1),
      (ch['report'], REPORT_WIDTH, 1),
      (_G.DERPY_TACTIC_LIST[ch['tactics']][:2], TACTIC_WIDTH, 1), (_G.DERPY_GROUND_TYPE[ch['forte']], FORTE_WIDTH, 1), 
      (spd_chr, SPEED_WIDTH, 1), (sta_chr, STAMINA_WIDTH, 1),
      (ch['condition'], CONDITION_WIDTH, 1), (_G.DERPY_WEATHER_TYPE[ch['weather']], WEATHER_WIDTH, 1),
      (ch['popularity'], POPULARITY_WIDTH, 1),
    ) + '\n'
  return string

def prediction_score2rank(race, predict, score_proc):
  scores = []
  ranks  = []
  for ch in race['character']:
    score, rank = score_proc(ch, predict)
    scores.append(score)
    ranks.append(rank)
  return (scores, ranks)

def rfr_time_scorerank(character, predict):
  order = sorted(predict, reverse=True)
  i = character['number'] - 1
  return ( int(predict[i]), next((n+1 for n,v in enumerate(order) if v == predict[i]), 0) )

def rfr_ord_scorerank(character, predict):
  order = sorted(predict)
  i = character['number'] - 1
  return ( "{:.3f}".format(predict[i]), next((n+1 for n,v in enumerate(order) if v == predict[i]), 0) )

def rfc_ord_scorerank(character, predict):
  i = character['number'] - 1
  return (predict[i], predict[i])

def make_predictions(race):
  score_proc = {
    f'{_G.DCTmpFolder}/rfr_fit_order_False-feats_all.mod': rfr_time_scorerank,
    f'{_G.DCTmpFolder}/rfr_fit_order_True-feats_all.mod': rfr_ord_scorerank,
    f'{_G.DCTmpFolder}/rfc_fit_order_True-feats_all.mod': rfc_ord_scorerank,
    f'{_G.DCTmpFolder}/knn_fit_order_True-feats_all.mod': rfc_ord_scorerank,
    f'{_G.DCTmpFolder}/rfr_fit_order_False-feats_noreport.mod': rfr_time_scorerank,
    f'{_G.DCTmpFolder}/rfr_fit_order_True-feats_noreport.mod': rfr_ord_scorerank,
    f'{_G.DCTmpFolder}/rfc_fit_order_True-feats_noreport.mod': rfc_ord_scorerank,
    f'{_G.DCTmpFolder}/knn_fit_order_True-feats_noreport.mod': rfc_ord_scorerank,
  }
  ret = []
  ranks = [np.array(range(1,len(race['character'])+1))]
  for model in ESTIMATORS:
    predict = predict_race(model, race)
    ret.append(predict)
    ranks.append(prediction_score2rank(race, predict, score_proc[model])[1])
    print('\n\n', model)
    print(predict)
    print(format_derpy_data(race, predict, score_proc[model]))
  for r in ranks:
    print(np.array(r))
  return ret
  
def main():
  race = get_upcoming_race()
  race = interpret_race_data(race)
  make_predictions(race)
  
if __name__ == '__main__':
  main()