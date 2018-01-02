import datetime
import logging
import os

import dill
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_FILE = '../data/final/counts/breast_cancer_counts.dill'
LOG_FILE = '../log/breast_cancer_counts_monthly_optimized_xgb.log'
RESULTS_FILE = '../log/breast_cancer_counts_monthly_optimized_results.dill'
N_JOBS = 30

rand_search = dill.load(open('../log/breast_cancer_counts_parameter_monthly_optim_xgb.dill', 'rb'))

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(message)s')

results = {}

data = dill.load(open(DATA_FILE, 'rb'))

results = {}
for months_before in sorted(list(data.keys())):
    print('\tMonth {}'.format(months_before))

    train_x = data[months_before]["TRAIN"]["X"]
    train_y = data[months_before]["TRAIN"]["y"]
    test_x = data[months_before]["TEST"]["X"]
    test_y = data[months_before]["TEST"]["y"]

    # Getting best params
    best_params = rand_search[months_before].best_params_
    best_params['random_state'] = 1
    best_params['n_jobs'] = N_JOBS

    # Creating and training model
    clf = XGBClassifier(**best_params)
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
