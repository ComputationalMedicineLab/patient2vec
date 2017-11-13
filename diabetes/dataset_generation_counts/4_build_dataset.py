import dill
import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from tqdm import tqdm

COUNTS_FILE = '../data/intermediate/diabetes_raw_counts.dill'
PATIENT_LIST = '../data/intermediate/patient_list_split.csv'
DATA_OUTPUT_FILE = '../data/final/counts/diabetes_counts.dill'

counts_dict = dill.load(open(COUNTS_FILE, 'rb'))
patient_list = pd.read_csv(PATIENT_LIST)
patient_groups = patient_list.groupby(by=['GROUP'])

data_patient_ids = []
data_patient_counts = []

for patient_id, counts in counts_dict.items():
    data_patient_ids.append(patient_id)
    data_patient_counts.append(counts)

dict_vectorizer = DictVectorizer(dtype=np.int, sparse=False, sort=True)
full_vector_data = dict_vectorizer.fit_transform(data_patient_counts)

data = {
    "TRAIN": {
        'X': [],
        'y': [],
        'vocabulary': dict_vectorizer.vocabulary_,
        'ids': []
    },
    "TEST": {
        'X': [],
        'y': [],
        'vocabulary': dict_vectorizer.vocabulary_,
        'ids': []
    },
    "VALIDATION": {
        'X': [],
        'y': [],
        'vocabulary': dict_vectorizer.vocabulary_,
        'ids': []
    }
}

for group in ['VALIDATION', 'TEST', 'TRAIN']:
    patients_df = patient_groups.get_group(group)
    patient_ids = patients_df['IND_SEQ'].values
    y = patients_df['OUTCOME'].values
    X = []
    for patient_id in tqdm(patient_ids):
        patient_data_index = data_patient_ids.index(patient_id)
        X.append(full_vector_data[patient_data_index])
    data[group]['X'] = np.array(X)
    data[group]['y'] = np.array(y, dtype=np.int)
    data[group]['ids'] = patient_ids

dill.dump(data, open(DATA_OUTPUT_FILE, 'wb'))
