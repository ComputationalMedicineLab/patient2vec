import datetime
import logging
import os

import dill
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_FILE = '../data/final/counts/diabetes_counts.dill'
LOG_FILE = '../../log/diabetes_counts_simple_rf.log'
N_JOBS = 15
N_ESTIMATORS = 2000

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# Loading data
data = dill.load(open(DATA_FILE, 'rb'))
train_x = data["TRAIN"]["X"]
train_y = data["TRAIN"]["y"]
test_x = data["TEST"]["X"]
test_y = data["TEST"]["y"]

# Creating and training model
clf = RandomForestClassifier(n_estimators=N_ESTIMATORS,
                             oob_score=True, random_state=1,
                             verbose=1, n_jobs=N_JOBS)
clf.fit(train_x, train_y)

# Scoring
pred_y = clf.predict_proba(test_x)

auc_score = roc_auc_score(test_y, pred_y[:,1])
log_score = log_loss(test_y, pred_y)

logging.info('auc: {}, log_loss: {}'.format(auc_score, log_score))
