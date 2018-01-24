import datetime
import logging
import os

import dill
import numpy as np
from scipy.stats import uniform

from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import RandomizedSearchCV

DATA_DIR = '../data/final/vectors_improved/'
OPTIM_FILE = '../log/lung_cancer_vectors_parameter_optim_elesticnet.dill'
N_JOBS = 30
N_RANDOM_SEARCH_ITER = 250
MONTHS = 12

param_dist = {
    "alpha": [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1],
    "l1_ratio": uniform()
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

data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.dill')]


for data_file in data_files:
    if data_file in optim_objects.keys():
        # Skip if already optimized
        print('Skipping {}'.format(data_file))
        continue

    print('Optimizing {}'.format(data_file))

    # Loading data
    data = dill.load(open(os.path.join(DATA_DIR, data_file), 'rb'))

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
    optim_objects[data_file] = random_search

dill.dump(optim_objects, open(OPTIM_FILE, 'wb'))
