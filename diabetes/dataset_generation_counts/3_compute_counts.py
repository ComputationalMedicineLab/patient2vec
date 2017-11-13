from collections import Counter

import dill
import pandas as pd
import numpy as np
from tqdm import tqdm

PATIENT_HISTORY_FILE = '../data/raw/diabetes_patients_codes.csv'
ICD_PHEWAS_MAP_FILE = '../data/intermediate/icd_phewas_map.csv'
MED_ATC_MAP_FILE = '../data/intermediate/generic_name_atc_map.csv'
COUNTS_OUTPUT_FILE = '../data/intermediate/diabetes_raw_counts.dill'


# ICD-9 to PHEWAS group dictionary
icd_phewas_map_df = pd.read_csv(ICD_PHEWAS_MAP_FILE)
icd_phewas_map = dict(zip(icd_phewas_map_df['ICD_CODE'].values.tolist(),
                          icd_phewas_map_df['PHEWAS_CODE'].values.tolist()))

# Drug name to ATC classes dictionary
med_atc_map_df = pd.read_csv(MED_ATC_MAP_FILE)
med_atc_map_pairs = zip(med_atc_map_df['GENERIC_NAME'].values.tolist(),
                        med_atc_map_df['ATC_CLASS'].values.tolist())
med_atc_map = {}
for med_atc_pair in med_atc_map_pairs:
    med = med_atc_pair[0]
    atc = med_atc_pair[1]
    if med in med_atc_map.keys():
        med_atc_map[med].append(atc)
    else:
        med_atc_map[med] = [atc]

# Reading file
tp = pd.read_csv(PATIENT_HISTORY_FILE, iterator=True, chunksize=10**5, sep='|', index_col=None, header=None)
patient_history_df = pd.concat(tp, ignore_index=True)
patient_history_df.columns = ["IND_SEQ", "ENTRY_DATE", "CODE", "TYPE"]
patient_history_groups_by_patient = patient_history_df.groupby(by=['IND_SEQ'])


def icd_to_phewas(icd_codes):
    global icd_phewas_map
    phewas_codes = []
    for code in icd_codes:
        if code in icd_phewas_map.keys():
            phewas_codes.append(icd_phewas_map[code])
    return phewas_codes

def meds_to_atc(meds):
    global med_atc_map
    atc_classes = []
    for med in meds:
        if med in med_atc_map.keys():
            atc_classes += med_atc_map[med]
    return atc_classes

counts_dict = {}

for patient, patient_history in tqdm(patient_history_groups_by_patient, total=len(patient_history_groups_by_patient), leave=True):
    patient_type_groups = patient_history.groupby(by=['TYPE'])
    phewas_codes = []
    atc_classes = []
    labs = []
    if 'icd' in patient_type_groups.groups.keys():
        icd_codes = patient_type_groups.get_group('icd')['CODE'].values.tolist()
        phewas_codes = icd_to_phewas(icd_codes)
    if 'med' in patient_type_groups.groups.keys():
        meds = patient_type_groups.get_group('med')['CODE'].values.tolist()
        atc_classes = meds_to_atc(meds)
    if 'lab' in patient_type_groups.groups.keys():
        labs = patient_type_groups.get_group('lab')['CODE'].values.tolist()
    counts_dict[patient] = dict(Counter(phewas_codes + atc_classes + labs))

dill.dump(counts_dict, open(COUNTS_OUTPUT_FILE, 'wb'))
