from copy import deepcopy
from glob import glob
import _G
import json, sys
import matplotlib
matplotlib.use('Agg')
from matplotlib import get_backend
import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.preprocessing import MultiLabelBinarizer
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
from sklearn.neural_network import MLPClassifier
import pickle
from pprint import pprint
import derpy_datamanager as ddm

N_JOBS  = next((int(n.split('=')[-1]) for n in sys.argv if 'njobs=' in n or 'njob=' in n), -1)
GRID_CV = 5
VERBOSE = any([k for k in ['-v', '--verbose'] if k in sys.argv])

print(f"Training model with njobs={N_JOBS}")

K_FOLD = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
MSK_FOLD = MultilabelStratifiedKFold(n_splits=3, shuffle=True, random_state=42)

FIT_ORDER = False # if false, try to predict the time needed to goal
TARGET_MODEL = ''
DIM_REDUCTION = None
FEATURE_SYMBOL = 'all'

PARAM_RFR = {
  'n_estimators':[10,25,50,75,100,150,200],
  'max_depth':[None,3,5,7,10,16], 
  'min_samples_split': [2,3,4],
  'random_state': [42],
}

PARAM_RFC = {
  'n_estimators':[10,25,50,75,100,150,200],
  'max_depth':[None,3,5,7,10,16], 
  'min_samples_split': [2,3,4],
  'random_state': [42],
}

PARAM_KNN = {
  'n_neighbors': [n+1 for n in range(8)], 
  'algorithm': ['ball_tree', 'kd_tree', 'brute']
}

PARAM_SVC = {
  'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
  'C': [0.01, 0.1, 1, 10]
}

PARAM_SVR = {
  'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
  'C': [0.01, 0.1, 1, 10],
  'epsilon': [0, 0.01, 0.1],
}

x_train  = []
y_train  = []
oy_train = []

def gather_data():
  files = glob(f"{_G.DCTmpFolder}/*derpy_warehouse.json")
  ret  = []
  for file in files:
    with open(file, 'r') as fp:
      for race in json.load(fp):
        race = ddm.interpret_race_data(race)
        ret.append(race)
  return ret

def load_data():
  global FEATURE_SYMBOL
  global x_train, y_train, oy_train
  sample_n = 0
  oy_train = []
  for data in gather_data():
    times = []
    for i,res in enumerate(data['result']):
      ch = data['character'][i]
      features = _G.extract_derpy_features(data, ch, FEATURE_SYMBOL)
      x_train.append(features)
      times.append(res['time'])
      sample_n += 1
    # end each uma
    oy_train.extend(deepcopy(times))
    if not FIT_ORDER:
      std, avg = np.std(times), np.average(times)
      efdn = 3 # effective decimal n
      times = [(n - avg) / std for n in times]
      times = [10**(efdn+1) - n*(10**(efdn)) for n in times]
      times = [n*n // (10**(efdn+2)) for n in times]
      y_train.extend(times)
    else:
      otimes = sorted(times)
      for t in times:
        y_train.append( next((i+1 for i,n in enumerate(otimes) if n == t), 0) )
  # end each race
  x_train = np.array(x_train)
  y_train = np.array(y_train, dtype=np.int32)
  oy_train = np.array(oy_train)
  print('X train:', x_train, 'Y train:', y_train, 'Original y train:', np.array(oy_train), sep='\n')

def main(outname, validate=True):
  global K_FOLD, MSK_FOLD, PARAM_RFR, VERBOSE, N_JOBS, GRID_CV
  global x_train, y_train
  load_data()
  clsier = None
  cls_scoring = 'accuracy'
  if TARGET_MODEL == 'rfc':
    clsier = GridSearchCV(
      estimator=RandomForestClassifier(),
      param_grid=PARAM_RFC,
      scoring=cls_scoring,
      cv=GRID_CV, verbose=VERBOSE, n_jobs=N_JOBS
    )
  elif TARGET_MODEL == 'rfr':
    cls_scoring = 'explained_variance'
    clsier = GridSearchCV(
      estimator=RandomForestRegressor(),
      param_grid=PARAM_RFR,
      scoring=cls_scoring, 
      cv=GRID_CV, verbose=VERBOSE, n_jobs=N_JOBS
    )
  elif TARGET_MODEL == 'knn':
    clsier = GridSearchCV(
      estimator=KNeighborsClassifier(),
      param_grid=PARAM_KNN,
      scoring=cls_scoring,
      cv=GRID_CV, verbose=VERBOSE, n_jobs=N_JOBS
    )
  elif TARGET_MODEL == 'svc':
    clsier = GridSearchCV(
      estimator=svm.SVC(),
      param_grid=PARAM_SVC,
      scoring=cls_scoring,
      cv=GRID_CV, verbose=VERBOSE, n_jobs=N_JOBS
    )
  elif TARGET_MODEL == 'svr':
    cls_scoring = 'explained_variance'
    clsier = GridSearchCV(
      estimator=svm.SVR(),
      param_grid=PARAM_SVR,
      scoring=cls_scoring, 
      cv=GRID_CV, verbose=VERBOSE, n_jobs=N_JOBS
    )
  else:
    print("Don't know how to train model:", TARGET_MODEL)
    exit()

  print(f"Training {outname}, samples=", y_train.shape)
  
  clsier.fit(x_train, y_train)
  
  print("Best params: ", clsier.best_params_)
  print("Result:")
  print(clsier.cv_results_)
  
  with open(outname, 'wb') as fp:
    pickle.dump(clsier, fp)

  if not validate:
    return
  
  # print("===== Start Cross-Vaildating =====")
  # scores = cross_val_score(clsier, x_train, y_train, scoring=cls_scoring, cv=K_FOLD, verbose=VERBOSE,n_jobs=N_JOBS)
  print(outname)
  # print("cross_val_score: ", scores)

if __name__ == '__main__':
  for menu in _G.DERPY_TRAINING_LIST:
    FIT_ORDER = menu['fit_order']
    TARGET_MODEL = menu['model']
    FEATURE_SYMBOL = menu['feats']
    x_train = []
    y_train = []
    oy_train = []
    fname = f"{_G.DCTmpFolder}/{_G.make_model_name(menu)}"
    main(fname)