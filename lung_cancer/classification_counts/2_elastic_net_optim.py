import datetime
import logging
import os

import dill
import numpy as np
from scipy.stats import uniform

from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import RandomizedSearchCV

DATA_FILE = '../data/final/counts/lung_cancer_counts.dill'
OPTIM_FILE = '../log/lung_cancer_counts_parameter_optim_elasticnet.dill'
N_JOBS = 30
N_RANDOM_SEARCH_ITER = 250
MONTHS = 12

param_dist = {
    "alpha": [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1],
    "l1_ratio": uniform()
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
clf = SGDClassifier(loss='log', class_weight="balanced", penalty='elasticnet',
                    random_state=1, max_iter=1000)
random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                   n_iter=N_RANDOM_SEARCH_ITER, n_jobs=N_JOBS)
random_search.fit(train_x, train_y)

# Displaying and saving results
report(random_search.cv_results_)
dill.dump(random_search, open(OPTIM_FILE, 'wb'))
