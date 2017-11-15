import datetime
import logging
import os

import dill
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_DIR = '../data/final/vectors/'
LOG_FILE = '../../log/diabetes_vectors_simple_rf.log'
N_JOBS = 15
N_ESTIMATORS = 2000

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


def exists_in_log_file(term):
    try:
        with open(LOG_FILE, 'r') as f:
            return (term in f.read())
    except:
        pass
    return False


data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.dill')]

for data_file in data_files:
    if exists_in_log_file(data_file):
        # Skip if already trained and tested
        print('Skipping {}'.format(data_file))
        continue

    print('Training on {}'.format(data_file))

    # Loading data
    data = dill.load(open(os.path.join(DATA_DIR, data_file), 'rb'))
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

    logging.info('data: {}, auc: {}, log_loss: {}'.format(data_file, auc_score, log_score))
