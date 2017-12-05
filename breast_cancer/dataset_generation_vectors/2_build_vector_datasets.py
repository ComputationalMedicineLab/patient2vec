import os

import dill
import pandas as pd
import numpy as np
import gensim
from tqdm import tqdm

MONTHS_BEFORE = [0, 1, 3, 6, 12]

PATIENT2VEC_MODEL_DIR = '../../patient2vec/models/'
PATIENT_LIST = '../data/intermediate/patient_list_split.csv'
PATIENT_DOCUMENTS = '../data/intermediate/breast_cancer_documents.dill'
VECTORS_OUTPUT_DIR = '../data/final/vectors'

patient_list = pd.read_csv(PATIENT_LIST)
patient_groups = patient_list.groupby(by=['GROUP'])
patient_documents = dill.load(open(PATIENT_DOCUMENTS, 'rb'))
model_list = [f for f in os.listdir(PATIENT2VEC_MODEL_DIR) if f.endswith('.gen')]


def get_vector_output_file_name(model_file):
    return 'vectors_{}.dill'.format(model_file.split('.')[0])

def file_exists(path):
    return os.path.isfile(path)

for model_file in model_list:
    if file_exists(os.path.join(VECTORS_OUTPUT_DIR, get_vector_output_file_name(model_file))):
        # Skip if already processed
        print('Skipping model {}'.format(model_file))
        continue

    print('Processing model {}'.format(model_file))

    # Loading model
    model = gensim.models.Doc2Vec.load(os.path.join(PATIENT2VEC_MODEL_DIR, model_file))
    vectors_dict = {k: {} for k in MONTHS_BEFORE}

    for months_before in MONTHS_BEFORE:
        print('Months before: {}'.format(months_before))
        for group in ['VALIDATION', 'TEST', 'TRAIN']:
            print('{}'.format(group))
            vectors_dict[months_before][group] = {'X': [], 'y': [], 'ids': []}
            patients_df = patient_groups.get_group(group)
            for patient_row in tqdm(patients_df.iterrows(), total=len(patients_df), leave=True):
                patient = patient_row[1]['IND_SEQ']
                patient_outcome = patient_row[1]['OUTCOME']
                patient_history = patient_documents[months_before][patient]
                patient_vector = model.infer_vector(patient_history)
                vectors_dict[months_before][group]['X'].append(patient_vector)
                vectors_dict[months_before][group]['y'].append(patient_outcome)
                vectors_dict[months_before][group]['ids'].append(patient)
            vectors_dict[months_before][group]['X'] = np.array(vectors_dict[months_before][group]['X'])
            vectors_dict[months_before][group]['y'] = np.array(vectors_dict[months_before][group]['y'])
            vectors_dict[months_before][group]['ids'] = np.array(vectors_dict[months_before][group]['ids'])

    # Save vectors
    dill.dump(vectors_dict, open(os.path.join(VECTORS_OUTPUT_DIR, get_vector_output_file_name(model_file)), 'wb'))
