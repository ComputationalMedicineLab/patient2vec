import datetime
import logging
import os

import dill
import numpy as np
from scipy.stats import randint

from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import RandomizedSearchCV

DATA_DIR = '../data/final/vectors_improved/'
data_files = [
    'vectors_patient2vec_pvdbow_hs_win-30_emb-100.dill',
    'vectors_patient2vec_pvdbow_hs_win-30_emb-50.dill',
    'vectors_patient2vec_pvdbow_hs_win-50_emb-100.dill',
    'vectors_patient2vec_pvdbow_hs_win-5_emb-100.dill',
]
MONTHS = [0, 1, 3, 6, 12]
OPTIM_FILE = '../log/lung_cancer_vectors_parameter_monthly_optim_xgb.dill'
N_JOBS = 30
N_RANDOM_SEARCH_ITER = 250

param_dist = {
    "max_depth": [5, 6, 7, 8, 9],
    "min_child_weight": [1, 2, 3, 4, 5],
    "gamma": [0, 0.1, 0.2],
    "subsample": [0.7, 0.8, 0.9],
    "colsample_bytree": [0.7, 0.8, 0.9, 1],
    "reg_alpha": [0, 0.0001, 0.001, 0.005, 0.01, 0.05, 0.1],
    "learning_rate": [0.01, 0.05],
    "n_estimators": [1000, 2000, 3000, 4000, 5000]
}

def file_exists(path):
    return os.path.isfile(path)

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


if file_exists(OPTIM_FILE):
    optim_objects = dill.load(open(OPTIM_FILE, 'rb'))
else:
    optim_objects = {}

for data_file in data_files:
    if data_file in optim_objects.keys():
        # Skip if already optimized
        print('Skipping {}'.format(data_file))
        continue

    print('Optimizing {}'.format(data_file))

    # Loading data
    data = dill.load(open(os.path.join(DATA_DIR, data_file), 'rb'))
    optim_objects[data_file] = {}

    for month in MONTHS:
        if month in optim_objects[data_file].keys():
            # Skip if already optimized
            print('\tSkipping month {}'.format(month))
            continue

        print('\tMonth {}'.format(month))
        train_x = data[month]["TRAIN"]["X"]
        train_y = data[month]["TRAIN"]["y"]

        # Parameter search
        clf = XGBClassifier(random_state=1, n_jobs=N_JOBS, silent=True)
        random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                           n_iter=N_RANDOM_SEARCH_ITER, verbose=1)
        random_search.fit(train_x, train_y)

        # Displaying and saving results
        report(random_search.cv_results_)
        optim_objects[data_file][month] = random_search
        dill.dump(optim_objects, open(OPTIM_FILE, 'wb'))

dill.dump(optim_objects, open(OPTIM_FILE, 'wb'))
