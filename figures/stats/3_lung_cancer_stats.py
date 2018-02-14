# CREATE TABLE p2v_lung_cancer_patients_stats AS
# (
# select p2v_lung_cancer_all_patients_events.ind_seq, p2v_lung_cancer_all_patients_events.entry_date, p2v_lung_cancer_all_patients_events.code,
# p2v_lung_cancer_all_patients_events.type, p2v_lung_cancer_patients_outcome.outcome from p2v_lung_cancer_all_patients_events
# join p2v_lung_cancer_patients_outcome on p2v_lung_cancer_all_patients_events.ind_seq = p2v_lung_cancer_patients_outcome.ind_seq
# )
# DELETE FROM p2v_lung_cancer_patients_stats where entry_date < '1987-01-01'

##### Positive!

    ## Number of event records (icd+med+lab):
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=1
    # 744,771
    ## Number of ICD-9 code records:
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=1 and type='icd'
    # 152,331
    ## Number of lab records:
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=1 and type='lab'
    # 445196
    ## Number of med records:
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=1 and type='med'
    # 147,244

    ## Distinct codes ('words'):
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=1
    # 7,694
    ## Distinct ICD-9 codes
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=1 and type='icd'
    # 5,600
    ## Distinct lab codes
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=1 and type='lab'
    # 1,038
    ## Distinct med codes
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=1 and type='med'
    # 1,056

    ## Number of patients:
    # select count(distinct ind_seq) from p2v_lung_cancer_patients_stats where outcome=1;
    # 1,104

##### Negative!

    ## Number of event records (icd+med+lab):
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=0
    # 5,803,625
    ## Number of ICD-9 code records:
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=0 and type='icd'
    # 1,059,198
    ## Number of lab records:
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=0 and type='lab'
    # 3,626,106
    ## Number of med records:
    # select count(*) from p2v_lung_cancer_patients_stats where outcome=0 and type='med'
    # 1,118,321

    ## Distinct codes ('words'):
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=0
    # 14,820/14,829
    ## Distinct ICD-9 codes
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=0 and type='icd'
    # 10,720
    ## Distinct lab codes
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=0 and type='lab'
    # 2,117
    ## Distinct med codes
    # select count(distinct code) from p2v_lung_cancer_patients_stats where outcome=0 and type='med'
    # 1,992

    ## Number of patients:
    # select count(distinct ind_seq) from p2v_lung_cancer_patients_stats where outcome=0;
    # 5,631


# 'lung_cancer_stats.csv' file
# select ind_seq, months_between(max(cutoff_date), min(entry_date)), count(*) as total_count,
# sum(case type when 'med' then 1 else 0 end) as med_count,  sum(case type when 'lab' then 1 else 0 end) as lab_count,
# sum(case type when 'icd' then 1 else 0 end) as icd_count, min(outcome) as outcome
# from p2v_lung_cancer_patients_stats group by ind_seq;

import numpy as np
import pandas as pd
from tqdm import *

STATS_FILE = 'lung_cancer_stats.csv'
stats_df = pd.read_csv(STATS_FILE, index_col=None)

outcome_groups = stats_df.groupby(by=["OUTCOME"])


for outcome, group_df in outcome_groups:
    print("Outcome: {}".format(outcome))

    ## Per patient
    for c in ['MONTHS_BETWEEN', 'TOTAL_COUNT', 'MED_COUNT', 'LAB_COUNT', 'ICD_COUNT']:
        print("{}:\t{:.1f} [{:.1f}, {:.1f}]".format(c, group_df[c].median(), group_df[c].quantile(0.25), group_df[c].quantile(0.75)))

## -- End pasted text --
# Outcome: 0
# MONTHS_BETWEEN:	71.6 [43.3, 114.2]
# TOTAL_COUNT:	369 [98, 1130.5]
# MED_COUNT:	54 [9, 201.5]
# LAB_COUNT:	208 [42, 674]
# ICD_COUNT:	92 [35, 231]
# Outcome: 1
# MONTHS_BETWEEN:	80.1 [49.9, 124.9]
# TOTAL_COUNT:	329.5 [104.8, 792.8]
# MED_COUNT:	49 [10, 157.5]
# LAB_COUNT:	183.5 [48.8, 466.2]
# ICD_COUNT:	79.5 [33, 174]
