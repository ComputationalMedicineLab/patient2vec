import datetime
import logging
import os

import dill
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_DIR = '../data/final/vectors_improved/'
LOG_FILE = '../log/breast_cancer_vectors_optimized_xgb.log'
RESULTS_FILE = '../log/breast_cancer_vectors_results.dill'
N_JOBS = 30

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(message)s')


def file_exists(path):
    return os.path.isfile(path)


def exists_in_log_file(term):
    try:
        with open(LOG_FILE, 'r') as f:
            return (term in f.read())
    except:
        pass
    return False


if file_exists(RESULTS_FILE):
    results = dill.load(open(RESULTS_FILE, 'rb'))
else:
    results = {}

vector_optim = dill.load(open('../log/breast_cancer_vectors_parameter_optim_xgb.dill', 'rb'))

for data_file, rand_search in vector_optim.items():
    if exists_in_log_file(data_file):
        # Skip if already trained and tested
        print('Skipping {}'.format(data_file))
        continue

    print('Training on {}.'.format(data_file))

    # Loading data
    data = dill.load(open(os.path.join(DATA_DIR, data_file), 'rb'))
    results[data_file] = {}
    for months_before in sorted(list(data.keys())):
        train_x = data[months_before]["TRAIN"]["X"]
        train_y = data[months_before]["TRAIN"]["y"]
        test_x = data[months_before]["TEST"]["X"]
        test_y = data[months_before]["TEST"]["y"]

        # Getting best params
        best_params = rand_search.best_params_
        best_params['random_state'] = 1
        best_params['n_jobs'] = N_JOBS

        # Creating and training model
        clf = XGBClassifier(**best_params)
        clf.fit(train_x, train_y, verbose=True)

        # Scoring
        pred_y = clf.predict_proba(test_x)

        auc_score = roc_auc_score(test_y, pred_y[:,1])
        log_score = log_loss(test_y, pred_y)

        results[data_file][months_before] = {}
        results[data_file][months_before]['true_y'] = test_y
        results[data_file][months_before]['pred_y'] = pred_y

        logging.info('{}, {}, {}, {}'.format(data_file, months_before, auc_score, log_score))

dill.dump(results, open(RESULTS_FILE, 'wb'))
