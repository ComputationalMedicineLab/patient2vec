# CREATE TABLE p2v_breast_cancer_patients_stats AS
# (
# select p2v_breast_cancer_all_patients_events.ind_seq, p2v_breast_cancer_all_patients_events.entry_date, p2v_breast_cancer_all_patients_events.code,
# p2v_breast_cancer_all_patients_events.type, p2v_breast_cancer_patients_outcome.outcome, p2v_breast_cancer_patients_outcome.cutoff_date from p2v_breast_cancer_all_patients_events
# join p2v_breast_cancer_patients_outcome on p2v_breast_cancer_all_patients_events.ind_seq = p2v_breast_cancer_patients_outcome.ind_seq
# )

##### Positive!

    ## Number of event records (icd+med+lab):
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=1
    # 1,276,676
    ## Number of ICD-9 code records:
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=1 and type='icd'
    # 300,226
    ## Number of lab records:
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=1 and type='lab'
    # 710,161
    ## Number of med records:
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=1 and type='med'
    # 266,289

    ## Distinct codes ('words'):
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=1
    # 9,666 / 9,671
    ## Distinct ICD-9 codes
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=1 and type='icd'
    # 7,094
    ## Distinct lab codes
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=1 and type='lab'
    # 1,240
    ## Distinct med codes
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=1 and type='med'
    # 1,337

    ## Number of patients:
    # select count(distinct ind_seq) from p2v_breast_cancer_patients_stats where outcome=1;
    # 2,901

##### Negative!

    ## Number of event records (icd+med+lab):
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=0
    # 1,313,530
    ## Number of ICD-9 code records:
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=0 and type='icd'
    # 300,248
    ## Number of lab records:
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=0 and type='lab'
    # 741,293
    ## Number of med records:
    # select count(*) from p2v_breast_cancer_patients_stats where outcome=0 and type='med'
    # 271,989

    ## Distinct codes ('words'):
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=0
    # 11,348
    ## Distinct ICD-9 codes
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=0 and type='icd'
    # 8,261
    ## Distinct lab codes
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=0 and type='lab'
    # 1,510
    ## Distinct med codes
    # select count(distinct code) from p2v_breast_cancer_patients_stats where outcome=0 and type='med'
    # 1,577

    ## Number of patients:
    # select count(distinct ind_seq) from p2v_breast_cancer_patients_stats where outcome=0;
    # 2,901


# 'breast_cancer_stats.csv' file
select ind_seq, months_between(max(cutoff_date), min(entry_date)), count(*) as total_count,
sum(case type when 'med' then 1 else 0 end) as med_count,  sum(case type when 'lab' then 1 else 0 end) as lab_count,
sum(case type when 'icd' then 1 else 0 end) as icd_count, min(outcome) as outcome
from p2v_breast_cancer_patients_stats group by ind_seq;

import numpy as np
import pandas as pd
from tqdm import *

STATS_FILE = 'breast_cancer_stats.csv'
stats_df = pd.read_csv(STATS_FILE, index_col=None)

outcome_groups = stats_df.groupby(by=["OUTCOME"])


for outcome, group_df in outcome_groups:
    print("Outcome: {}".format(outcome))

    ## Per patient
    for c in ['MONTHS_BETWEEN', 'TOTAL_COUNT', 'MED_COUNT', 'LAB_COUNT', 'ICD_COUNT']:
        print("{}:\t{:.1f} [{:.1f}, {:.1f}]".format(c, group_df[c].median(), group_df[c].quantile(0.25), group_df[c].quantile(0.75)))

# Outcome: 0
# MONTHS_BETWEEN:	143.2 [100.9, 186.7]
# TOTAL_COUNT:	163 [64, 475]
# MED_COUNT:	26 [7, 88]
# LAB_COUNT:	78 [13, 261]
# ICD_COUNT:	51 [25, 122]
# Outcome: 1
# MONTHS_BETWEEN:	90.1 [55.6, 132.5]
# TOTAL_COUNT:	168 [59, 461]
# MED_COUNT:	23 [4, 87]
# LAB_COUNT:	85 [18, 247]
# ICD_COUNT:	51 [25, 122]
