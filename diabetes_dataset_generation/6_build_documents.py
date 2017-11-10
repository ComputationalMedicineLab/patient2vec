import dill
import pandas as pd
from tqdm import tqdm

PATIENT_HISTORY_FILE = '../data/raw/diabetes_patients_codes.csv'
DOCUMENTS_OUTPUT_FILE = '../data/intermediate/diabetes_documents.dill'

tp = pd.read_csv(PATIENT_HISTORY_FILE, iterator=True, chunksize=10**5, sep='|', index_col=None, header=None)
patient_history_df = pd.concat(tp, ignore_index=True)
patient_history_df.columns = ["IND_SEQ", "ENTRY_DATE", "CODE", "TYPE"]
patient_history_groups_by_patient = patient_history_df.groupby(by=['IND_SEQ'])

documents = {}

for patient, patient_history in tqdm(patient_history_df.groupby(by=['IND_SEQ']), leave=True):
    patient_codes = patient_history['CODE'].values.tolist()
    documents[patient] = patient_codes

dill.dump(documents, open(DOCUMENTS_OUTPUT_FILE, 'wb'))
