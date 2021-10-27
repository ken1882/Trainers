from copy import deepcopy
import _G
import json, sys
import matplotlib
matplotlib.use('Agg')
from matplotlib import get_backend
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.preprocessing import MultiLabelBinarizer
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
import pickle
from pprint import pprint

N_JOBS  = -1
GRID_CV = 5
VERBOSE = any([k for k in ['-v', '--verbose'] if k in sys.argv])

OUTPUT_NAME = _G.DERPY_RFR_MODEL_NAME

K_FOLD = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
MSK_FOLD = MultilabelStratifiedKFold(n_splits=3, shuffle=True, random_state=42)

FIT_ORDER = False # if false, try to predict the time needed to goal

PARAM_RFR = {
  'n_estimators':[50,75,100,150,200],
  'max_depth':[None,3,5,7,10,16], 
  'min_samples_split': [2,3,4],
  'random_state': [42],
}

x_train = []
y_train = []

def load_data():
  global x_train, y_train
  sample_n = 0
  ori_y = []
  with open(_G.DERPY_WAREHOUSE_CONTENT_PATH, 'r') as fp:
    for line in fp:
      times = []
      data  = json.loads(line)
      n_uma = len(data['result'])
      for i,res in enumerate(data['result']):
        ch = data['character'][i]
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
        times.append(res['time'])
        sample_n += 1
      # end each uma
      ori_y.extend(deepcopy(times))
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
  print('X train:', x_train, 'Y train:', y_train, 'Original y train:', ori_y, sep='\n')

def main():
  global K_FOLD, MSK_FOLD, PARAM_RFR, VERBOSE, N_JOBS, GRID_CV
  global x_train, y_train
  
  load_data()
  clsier = None
  if FIT_ORDER:
    pass
  else:
    cls_scoring = 'scoring'
    clsier = GridSearchCV(
      estimator=RandomForestRegressor(), param_grid=PARAM_RFR,
      scoring=cls_scoring, 
      cv=GRID_CV, verbose=VERBOSE, n_jobs=N_JOBS
    )
  
  print("Training Random Forest, samples=", y_train.shape)
  
  clsier.fit(x_train, y_train)
  
  print("Best params: ", clsier.best_params_)
  print("Result:")
  print(clsier.cv_results_)
  
  with open(OUTPUT_NAME, 'wb') as fp:
    pickle.dump(clsier, fp)
  
  # with open(OUTPUT_NAME, 'rb') as fp:
  #   clsier_rfr = pickle.load(fp)

  print("===== Start Cross-Vaildating =====")

  scores = cross_val_score(clsier, x_train, y_train, scoring=cls_scoring, cv=K_FOLD, verbose=VERBOSE,n_jobs=N_JOBS)
  print("cross_val_score: ", scores)

if __name__ == '__main__':
  main()