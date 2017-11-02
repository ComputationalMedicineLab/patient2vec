# Generates documents

from concurrent.futures import ProcessPoolExecutor, as_completed

import dill
from gensim.models.doc2vec import LabeledSentence
import numpy as np
import pandas as pd
from tqdm import *

WORKERS = 45
INPUT_FILE = "../data/raw/all_patients_events_combined.csv"
DOCUMENTS_FILE = "../data/final/patient2vec_documents.dill"

print("Loading input file...")
tp = pd.read_csv(INPUT_FILE, iterator=True, chunksize=10**5, sep='|', index_col=None, header=None)
df = pd.concat(tp, ignore_index=True)
df.columns = ["IND_SEQ", "ENTRY_DATE", "CODE"]

print("Dividing data frame into groups...")
patient_groups = df.groupby(by=["IND_SEQ"])
documents = []


def generate_document(ind_seq, patient_df):
    document = []
    patient_day_groups = patient_df.groupby(by=["ENTRY_DATE"])
    for _, day_df in patient_day_groups:
        day_codes = np.unique(day_df["CODE"].astype(str).values)
        document += day_codes.tolist()
    return LabeledSentence(words=document, tags=[str(ind_seq)])


process_pool = ProcessPoolExecutor(WORKERS)
futures = []

print("Submitting jobs to the queue...")
for ind_seq, patient_df in tqdm(patient_groups, leave=True, total=len(patient_groups)):
    futures.append(process_pool.submit(generate_document, ind_seq, patient_df))

print("Processing data...")
for future_result in tqdm(as_completed(futures), leave=True, total=len(patient_groups)):
    documents.append(future_result.result())

print("Saving documents...")
dill.dump(documents, open(DOCUMENTS_FILE, "wb"))
