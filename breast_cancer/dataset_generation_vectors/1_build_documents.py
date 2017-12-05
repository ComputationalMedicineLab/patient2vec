import arrow
import dill
import pandas as pd
from tqdm import tqdm

MONTHS_BEFORE = [0, 1, 3, 6, 12]

PATIENT_LIST_FILE = '../data/intermediate/patient_list.csv'
PATIENT_HISTORY_FILE = '../data/raw/breast_cancer_patients_codes.csv'
DOCUMENTS_OUTPUT_FILE = '../data/intermediate/breast_cancer_documents.dill'

patient_list_df = pd.read_csv(PATIENT_LIST_FILE)
patient_cutoff_map = dict(zip(patient_list_df['IND_SEQ'].values.tolist(),
                              patient_list_df['CUTOFF_DATE'].values.tolist()))

tp = pd.read_csv(PATIENT_HISTORY_FILE, iterator=True, chunksize=10**5, sep='|', index_col=None, header=None)
patient_history_df = pd.concat(tp, ignore_index=True)
patient_history_df.columns = ["IND_SEQ", "ENTRY_DATE", "CODE", "TYPE"]
patient_history_groups_by_patient = patient_history_df.groupby(by=['IND_SEQ'])

documents = {k: {} for k in MONTHS_BEFORE}

for patient, patient_history in tqdm(patient_history_df.groupby(by=['IND_SEQ']), leave=True):
    for months_before in MONTHS_BEFORE:
        patients_cutoff_date = arrow.get(patient_cutoff_map[patient])
        patients_shifted_date = patients_cutoff_date.shift(months=-months_before).format('YYYY-MM-DD')
        patient_history_cut = patient_history[patient_history['ENTRY_DATE'] <= patients_shifted_date]

        patient_codes = patient_history_cut['CODE'].values.tolist()
        documents[months_before][patient] = patient_codes

dill.dump(documents, open(DOCUMENTS_OUTPUT_FILE, 'wb'))
