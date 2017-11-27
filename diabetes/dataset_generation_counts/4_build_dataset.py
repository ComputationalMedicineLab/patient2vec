import dill
import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from tqdm import tqdm

MONTHS_BEFORE = [0, 1, 3, 6, 12]

COUNTS_FILE = '../data/intermediate/diabetes_raw_counts.dill'
PATIENT_LIST = '../data/intermediate/patient_list_split.csv'
DATA_OUTPUT_FILE = '../data/final/counts/diabetes_counts.dill'

counts_dict = dill.load(open(COUNTS_FILE, 'rb'))
patient_list = pd.read_csv(PATIENT_LIST)
patient_groups = patient_list.groupby(by=['GROUP'])

data_patient_ids = {k: [] for k in MONTHS_BEFORE}
data_patient_counts = {k: [] for k in MONTHS_BEFORE}
dict_vectorizers = {k: None for k in MONTHS_BEFORE}
full_vector_data = {k: None for k in MONTHS_BEFORE}

for months_before in MONTHS_BEFORE:
    for patient_id, counts in counts_dict[months_before].items():
        data_patient_ids[months_before].append(patient_id)
        data_patient_counts[months_before].append(counts)

    dict_vectorizers[months_before] = DictVectorizer(dtype=np.int, sparse=False, sort=True)
    full_vector_data[months_before] = dict_vectorizers[months_before].fit_transform(data_patient_counts[months_before])


data = {}
for months_before in MONTHS_BEFORE:
    data[months_before] = {
        "TRAIN": {
            'X': [],
            'y': [],
            'vocabulary': dict_vectorizers[months_before].vocabulary_,
            'ids': []
        },
        "TEST": {
            'X': [],
            'y': [],
            'vocabulary': dict_vectorizers[months_before].vocabulary_,
            'ids': []
        },
        "VALIDATION": {
            'X': [],
            'y': [],
            'vocabulary': dict_vectorizers[months_before].vocabulary_,
            'ids': []
        }
    }

for months_before in MONTHS_BEFORE:
    for group in ['VALIDATION', 'TEST', 'TRAIN']:
        patients_df = patient_groups.get_group(group)
        patient_ids = patients_df['IND_SEQ'].values
        y = patients_df['OUTCOME'].values
        X = []
        for patient_id in tqdm(patient_ids):
            patient_data_index = data_patient_ids[months_before].index(patient_id)
            X.append(full_vector_data[months_before][patient_data_index])
        data[months_before][group]['X'] = np.array(X)
        data[months_before][group]['y'] = np.array(y, dtype=np.int)
        data[months_before][group]['ids'] = patient_ids

dill.dump(data, open(DATA_OUTPUT_FILE, 'wb'))
