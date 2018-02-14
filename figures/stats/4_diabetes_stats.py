# CREATE TABLE p2v_diabetes_patients_stats AS
# (
# select p2v_diabetes_all_patients_events_2.ind_seq, p2v_diabetes_all_patients_events_2.entry_date, p2v_diabetes_all_patients_events_2.code,
# p2v_diabetes_all_patients_events_2.type, p2v_patients_outcome.outcome, p2v_patients_outcome.cutoff_date from p2v_diabetes_all_patients_events_2
# join p2v_patients_outcome on p2v_diabetes_all_patients_events_2.ind_seq = p2v_patients_outcome.ind_seq
# )

##### Positive!

    ## Number of event records (icd+med+lab):
    # select count(*) from p2v_diabetes_patients_stats where outcome=1
    # 2,627,275
    ## Number of ICD-9 code records:
    # select count(*) from p2v_diabetes_patients_stats where outcome=1 and type='icd'
    # 683,538
    ## Number of lab records:
    # select count(*) from p2v_diabetes_patients_stats where outcome=1 and type='lab'
    # 1476329
    ## Number of med records:
    # select count(*) from p2v_diabetes_patients_stats where outcome=1 and type='med'
    # 467408

    ## Distinct codes ('words'):
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=1
    # 12620/12625
    ## Distinct ICD-9 codes
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=1 and type='icd'
    # 9459
    ## Distinct lab codes
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=1 and type='lab'
    # 1643
    ## Distinct med codes
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=1 and type='med'
    # 1523

    ## Number of patients:
    # select count(distinct ind_seq) from p2v_diabetes_patients_stats where outcome=1;
    # 10477

##### Negative!

    ## Number of event records (icd+med+lab):
    # select count(*) from p2v_diabetes_patients_stats where outcome=0
    # 2699443
    ## Number of ICD-9 code records:
    # select count(*) from p2v_diabetes_patients_stats where outcome=0 and type='icd'
    # 683542
    ## Number of lab records:
    # select count(*) from p2v_diabetes_patients_stats where outcome=0 and type='lab'
    # 1554251
    ## Number of med records:
    # select count(*) from p2v_diabetes_patients_stats where outcome=0 and type='med'
    # 461650

    ## Distinct codes ('words'):
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=0
    # 14755/14756
    ## Distinct ICD-9 codes
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=0 and type='icd'
    # 10933
    ## Distinct lab codes
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=0 and type='lab'
    # 1949
    ## Distinct med codes
    # select count(distinct code) from p2v_diabetes_patients_stats where outcome=0 and type='med'
    # 1874

    ## Number of patients:
    # select count(distinct ind_seq) from p2v_diabetes_patients_stats where outcome=0;
    # 10477


# 'diabetes_stats.csv' file
# select ind_seq, months_between(max(cutoff_date), min(entry_date)), count(*) as total_count,
# sum(case type when 'med' then 1 else 0 end) as med_count,  sum(case type when 'lab' then 1 else 0 end) as lab_count,
# sum(case type when 'icd' then 1 else 0 end) as icd_count, min(outcome) as outcome
# from p2v_diabetes_patients_stats group by ind_seq;

import numpy as np
import pandas as pd
from tqdm import *

STATS_FILE = 'diabetes_stats.csv'
stats_df = pd.read_csv(STATS_FILE, index_col=None)

outcome_groups = stats_df.groupby(by=["OUTCOME"])


for outcome, group_df in outcome_groups:
    print("Outcome: {}".format(outcome))

    ## Per patient
    for c in ['MONTHS_BETWEEN', 'TOTAL_COUNT', 'MED_COUNT', 'LAB_COUNT', 'ICD_COUNT']:
        print("{}:\t{:.1f} [{:.1f}, {:.1f}]".format(c, group_df[c].median(), group_df[c].quantile(0.25), group_df[c].quantile(0.75)))

# Outcome: 0
# MONTHS_BETWEEN:	129.1 [87.5, 173.6]
# TOTAL_COUNT:	114 [49, 265]
# MED_COUNT:	16 [4, 46]
# LAB_COUNT:	48 [2, 143]
# ICD_COUNT:	39 [21, 76]
# Outcome: 1
# MONTHS_BETWEEN:	70 [42.7, 110]
# TOTAL_COUNT:	118 [50, 275]
# MED_COUNT:	11 [2, 43]
# LAB_COUNT:	60 [8, 155]
# ICD_COUNT:	39 [21, 76]
