import datetime
import logging
import os

import dill
import numpy as np
from scipy.stats import randint

from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV

DATA_FILE = '../data/final/counts/lung_cancer_counts.dill'
OPTIM_FILE = '../log/lung_cancer_counts_parameter_optim_xgb.dill'
N_JOBS = 32
N_RANDOM_SEARCH_ITER = 250
MONTHS = 12

param_dist = {
    "max_depth": randint(3, 10),
    "min_child_weight": randint(1, 6),
    "gamma": [0, 0.1, 0.2],
    "subsample": [0.7, 0.8, 0.9, 1],
    "colsample_bytree": [0.7, 0.8, 0.9, 1],
    "reg_alpha": [0, 0.0001, 0.001, 0.005, 0.01, 0.05, 0.1],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "n_estimators": [100, 500, 1000, 2000, 3000, 4000, 5000]
}

def report(results, n_top=4):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")

# Loading data
data = dill.load(open(DATA_FILE, 'rb'))

train_x = data[MONTHS]["TRAIN"]["X"]
train_y = data[MONTHS]["TRAIN"]["y"]

# Parameter search
clf = XGBClassifier(random_state=1, n_jobs=N_JOBS, silent=False)
random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                   n_iter=N_RANDOM_SEARCH_ITER)
random_search.fit(train_x, train_y)

# Displaying and saving results
report(random_search.cv_results_)
dill.dump(random_search, open(OPTIM_FILE, 'wb'))
