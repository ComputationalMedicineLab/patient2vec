import datetime
import logging
import os

import dill
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_DIR = '../data/final/vectors_improved/'
LOG_FILE = '../log/diabetes_vectors_monthly_optimized_xgb.log'
RESULTS_FILE = '../log/diabetes_vectors_monthly_optimized_results.dill'
N_JOBS = 30

data_files = [
    'vectors_patient2vec_pvdbow_hs_win-30_emb-100.dill',
    'vectors_patient2vec_pvdbow_hs_win-30_emb-50.dill',
    'vectors_patient2vec_pvdbow_hs_win-50_emb-100.dill',
    'vectors_patient2vec_pvdbow_hs_win-5_emb-100.dill',
]

rand_search = dill.load(open('../log/diabetes_vectors_parameter_monthly_optim_xgb.dill', 'rb'))

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(message)s')


results = {}


for data_file in data_files:
    print('Training on {}.'.format(data_file))

    # Loading data
    data = dill.load(open(os.path.join(DATA_DIR, data_file), 'rb'))
    results[data_file] = {}
    for months_before in sorted(list(data.keys())):
        print('\tMonth {}'.format(months_before))

        train_x = data[months_before]["TRAIN"]["X"]
        train_y = data[months_before]["TRAIN"]["y"]
        test_x = data[months_before]["TEST"]["X"]
        test_y = data[months_before]["TEST"]["y"]

        # Getting best params
        best_params = rand_search[data_file][months_before].best_params_
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
