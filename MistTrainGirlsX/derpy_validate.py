# since only care the first 3 places most of time
# so this validation is based on it.

import os
import _G
import matplotlib
matplotlib.use('Agg')
from matplotlib import get_backend
import matplotlib.pyplot as plt
import json
import pickle
from glob import glob
import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.preprocessing import MultiLabelBinarizer
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
from sklearn.neural_network import MLPClassifier
import derpy_datamanager as ddm
from pprint import pprint

FIT_ORDER = False # if false, try to predict the time needed to goal
TARGET_MODEL = ''
DIM_REDUCTION = None
FEATURE_SYMBOL = 'all'

ESTIMATORS = [f"{_G.DCTmpFolder}/{_G.make_model_name(d)}" for d in _G.DERPY_TRAINING_LIST]

def gather_data():
    files = glob(f"{_G.DCTmpFolder}/*derpy_warehouse.json")
    ret  = []
    for file in files:
        with open(file, 'r') as fp:
            for race in json.load(fp):
                race = ddm.interpret_race_data(race)
                ret.append(race)
    return ret

def predict_race(estimator, race):
    global FIT_ORDER,TARGET_MODEL,FEATURE_SYMBOL
    x_train = []
    data = race['schedule'] if 'schedule' in race else race
    for ch in race['character']:
        features = _G.extract_derpy_features(data, ch, FEATURE_SYMBOL)
        x_train.append(features)
    
    return estimator.predict(x_train)

def pred_score2rank(scores):
    global FIT_ORDER,TARGET_MODEL
    ModelScoreProc = {
        'ft-rfr': rfr_time_scorerank,
        'fo-rfr': rfr_ord_scorerank,
        'fo-rfc': rfc_ord_scorerank,
        'fo-knn': rfc_ord_scorerank
    }
    ft = 'fo' if FIT_ORDER else 'ft'
    proc = ModelScoreProc[f"{ft}-{TARGET_MODEL}"]
    return [int(proc(i,scores)[1]) for i,s in enumerate(scores)]

# 0=score 1=rank
def rfr_time_scorerank(i, scores):
  order = sorted(scores, reverse=True)
  return ( int(scores[i]), next((n+1 for n,v in enumerate(order) if v == scores[i]), 0) )

def rfr_ord_scorerank(i, scores):
  order = sorted(scores)
  return ( "{:.3f}".format(scores[i]), next((n+1 for n,v in enumerate(order) if v == scores[i]), 0) )

def rfc_ord_scorerank(i, scores):
  return (scores[i], scores[i])

def determine_score(esti, result):
    global FIT_ORDER,TARGET_MODEL,FEATURE_SYMBOL
    ranks = pred_score2rank(esti)
    minn  = min(ranks) - 1
    ranks = [n-minn for n in ranks]
    ranks_real = [r['rank'] for r in result]
    base = 0
    hit  = 0
    for i,nth in enumerate(ranks):
        if nth <= 3:
            base += 1
        if nth <= 3 and ranks_real[i] <= 3:
            hit  += 1
    if base == 0 or any([n <= 0 for n in ranks]):
        print("[Warning] Invalid prediction")
        print(esti)
        print(ranks, ranks_real)
        return 0
    return hit / base


def validate_score(data, model):
    sum   = 0
    for race in data:
        est = predict_race(model, race)
        sum += determine_score(est, race['result'])
    return sum

def calc_accuracy():
  db = _G.DerpySavedRaceContent
  base = 0
  hit  = 0
  out  = open('.tmp.txt', 'w')
  for month in db:
    for race in db[month]:
      for i,ch in enumerate(race['character']):
        if ch['popularity'] <= 3:
          out.write(f"{ch}\n{race['result'][i]}\n")
          base += 1
          if race['result'][i]['rank'] <= 3:
            hit += 1
            out.write(">>> HIT <<<\n")
          else:
            out.write(">>> MISS <<<\n")
          out.write('-'*20+'\n')
  out.close()
  print(hit, base)
  return hit / base


def get_popularity_accuracy(data):
    base = 0
    hit  = 0
    for race in data:
        for i,ch in enumerate(race['character']):
            if ch['popularity'] <= 3:
                base += 1
                if race['result'][i]['rank'] <= 3:
                    hit  += 1
    return hit / base

def main():
    global FIT_ORDER,TARGET_MODEL,FEATURE_SYMBOL
    data = gather_data()
    for menu in _G.DERPY_TRAINING_LIST:
        fname = f"{_G.DCTmpFolder}/{_G.make_model_name(menu)}"
        if not os.path.exists(fname):
            print(f"[Warning] {fname} does not exists, skip")
            continue
        with open(fname, 'rb') as fp:
            model = pickle.load(fp)
        FIT_ORDER = menu['fit_order']
        TARGET_MODEL = menu['model']
        FEATURE_SYMBOL = menu['feats']
        print("Validating", fname)
        sum = validate_score(data, model)
        print(f"Score of {fname}: {sum / len(data)} (out of {len(data)} races)")

    print('-'*20)
    print("Popularity accuracy:", get_popularity_accuracy(data))

if __name__ == '__main__':
    main()
