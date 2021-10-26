import matplotlib
matplotlib.use('Agg')
from matplotlib import get_backend
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score