import logging
import os

import dill
from gensim.models.doc2vec import *

DOCUMENTS_FILE = "../data/final/patient2vec_documents.dill"
MODELS_DIR = "../models/patient2vec"

SEED = 1
WORKERS = 240
INITIAL_LEARNING_RATE = 0.025
MINIMAL_LEARNING_RATE = 0.0005
TRAIN_ITERATIONS = 100
MIN_COUNT = 250

optim_training_algos = ["pvdm", "pvdbow"]
optim_embedding_sizes = [100, 300, 500]
optim_window_sizes = [50, 30, 100]
optim_softmax_methods = ["hs", "ns"]

documents = dill.load(open(DOCUMENTS_FILE, "rb"))


def get_model_file_name(softmax_method, window_size, embedding_size, training_algo):
    file_name = "patient2vec_{}_{}_win-{}_emb-{}.gen".format(training_algo, softmax_method, window_size, embedding_size)
    return os.path.join(MODELS_DIR, file_name)


def file_exists(path):
    return os.path.isfile(path)


def train_model(softmax_method, window_size, embedding_size, training_algo):
    model_path = get_model_file_name(softmax_method, window_size, embedding_size, training_algo)
    if file_exists(model_path):
        print("{} already exists.".format(model_path))
        return

    print("Training {}.".format(model_path))
    dm = 1 if training_algo == "pvdm" else 0
    hs = 1 if softmax_method == "hs" else 0
    model = Doc2Vec(documents, dm=dm, size=embedding_size, alpha=INITIAL_LEARNING_RATE,
                    window=window_size, min_count=MIN_COUNT, seed=SEED,
                    workers=WORKERS, min_alpha=MINIMAL_LEARNING_RATE,
                    hs=hs, iter=TRAIN_ITERATIONS)

    model.save(model_path)


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

for softmax_method in optim_softmax_methods:
    for window_size in optim_window_sizes:
        for embedding_size in optim_embedding_sizes:
            for training_algo in optim_training_algos:
                train_model(softmax_method, window_size, embedding_size, training_algo)
