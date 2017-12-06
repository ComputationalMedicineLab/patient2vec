import datetime
import logging
import os

import dill
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_FILE = '../data/final/counts/lung_cancer_counts.dill'
LOG_FILE = '../log/lung_cancer_counts_simple_xgb.log'
N_JOBS = 30
N_ESTIMATORS = 2000

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
    clf = XGBClassifier(n_estimators=N_ESTIMATORS, random_state=1,
                        verbose=1, n_jobs=N_JOBS)
    clf.fit(train_x, train_y, verbose=True)

    # Scoring
    pred_y = clf.predict_proba(test_x)

    auc_score = roc_auc_score(test_y, pred_y[:,1])
    log_score = log_loss(test_y, pred_y)

    logging.info('{}, {}, {}'.format(months_before, auc_score, log_score))
