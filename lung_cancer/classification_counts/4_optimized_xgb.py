import datetime
import logging
import os

import dill
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_FILE = '../data/final/counts/lung_cancer_counts.dill'
LOG_FILE = '../log/lung_cancer_counts_optimized_xgb.log'
RESULTS_FILE = '../log/lung_cancer_counts_results.dill'
N_JOBS = 30

optimized_params = {
    'colsample_bytree': 1,
    'gamma': 0,
    'learning_rate': 0.01,
    'max_depth': 4,
    'min_child_weight': 4,
    'n_estimators': 500,
    'reg_alpha': 0.001,
    'subsample': 0.8,
    # other params:
    'random_state': 1,
    'silent': False,
    'n_jobs': N_JOBS
}

results = {}

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(message)s')

# Loading data
data = dill.load(open(DATA_FILE, 'rb'))

for months_before in sorted(list(data.keys())):
    train_x = data[months_before]["TRAIN"]["X"]
    train_y = data[months_before]["TRAIN"]["y"]
    test_x = data[months_before]["TEST"]["X"]
    test_y = data[months_before]["TEST"]["y"]

    # Creating and training model
    clf = XGBClassifier(**optimized_params)
    clf.fit(train_x, train_y, verbose=True)

    # Scoring
    pred_y = clf.predict_proba(test_x)

    auc_score = roc_auc_score(test_y, pred_y[:,1])
    log_score = log_loss(test_y, pred_y)

    results[months_before] = {}
    results[months_before]['true_y'] = test_y
    results[months_before]['pred_y'] = pred_y

    logging.info('{}, {}, {}'.format(months_before, auc_score, log_score))

dill.dump(results, open(RESULTS_FILE, 'wb'))
