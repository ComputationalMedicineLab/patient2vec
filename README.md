# patient2vec

## Project structure

* `patient2vec` directory contains all steps and scripts to train patient2vec models
  - `data` - directory for data (empty before data generation step)
  - `models` - directory for trained models (empty before training)
  - `dataset_generation` - contains queries and scripts to download and process data
  - `train_models` - contains script for training multiple patient2vec models
* `diabetes`
  - `data` - directory for data (mostly empty before data generation step)
  - `dataset_generation` - contains scripts, notebooks and queries to download data, select and split cohorts
  - `dataset_generation_vectors` - contains scripts to generate patient2vec vector based data; requires models in `/patient2vec/models` directory
  - `dataset_generation_counts` - contains scripts to generate PHEWAS, ATC counts data
  - `classification_counts` - contains scripts to train and test classification models on count based data
  - `classification_vactors` - contains scripts to train and test classification models on vector based data
