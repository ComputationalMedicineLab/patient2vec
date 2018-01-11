import datetime
import logging
import os

import dill
import numpy as np
from scipy.stats import randint

from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV

DATA_FILE = '../data/final/counts/diabetes_counts.dill'
OPTIM_FILE = '../log/diabetes_counts_parameter_monthly_optim_xgb.dill'
N_JOBS = 30
N_RANDOM_SEARCH_ITER = 100
MONTHS = [0, 1, 3, 6, 12]

param_dist = {
    "max_depth": [5, 6, 7, 8, 9],
    "min_child_weight": [1, 2, 3, 4],
    "gamma": [0, 0.1, 0.2],
    "subsample": [0.7, 0.8, 0.9],
    "colsample_bytree": [0.8, 0.9, 1],
    "reg_alpha": [0, 0.0001, 0.001, 0.005, 0.01],
    "learning_rate": [0.01],
    "n_estimators": [2000, 3000, 4000]
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

optim_objects = {}

for month in MONTHS:
    print('Month {}'.format(month))
    train_x = data[month]["TRAIN"]["X"]
    train_y = data[month]["TRAIN"]["y"]

    # Parameter search
    clf = XGBClassifier(random_state=1, n_jobs=N_JOBS, silent=True)
    random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                       n_iter=N_RANDOM_SEARCH_ITER)
    random_search.fit(train_x, train_y)

    # Displaying and saving results
    report(random_search.cv_results_)
    optim_objects[month] = random_search

dill.dump(optim_objects, open(OPTIM_FILE, 'wb'))
