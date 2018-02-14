# CREATE TABLE p2v_all_patients_events_combined_2 AS
# (
# 	SELECT * FROM
# 	(
# 	  (SELECT DISTINCT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, code, 'icd' as type FROM icd_codes)
# 	  UNION ALL
# 	  (SELECT DISTINCT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, test_sname AS code, 'lab' as type FROM labs_num)
# 	  UNION ALL
# 	  (
# 	    SELECT DISTINCT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, generic_name AS code, 'med' as type FROM medex
# 	      WHERE drug_strength <> '' AND drug_strength IS NOT NULL AND route <> ''
# 	      AND route IS NOT NULL AND drug_freq <> '' AND drug_freq IS NOT NULL
# 	      AND generic_name IS NOT NULL AND generic_name <> ''
# 	  )
# 	  ORDER BY ind_seq, entry_date
# 	) as foo
# 	WHERE ind_seq in (SELECT ind_seq FROM p2v_all_patients_events_combined)
# 	AND entry_date <= (SELECT max(entry_date) FROM p2v_all_patients_events_combined)
# )
# delete from p2v_all_patients_events_combined_2 where entry_date < '1987-01-01'

## Number of event records (icd+med+lab):
# select count(*) from p2v_all_patients_events_combined_2
# 362,528,405
## Number of ICD-9 code records:
# select count(*) from p2v_all_patients_events_combined_2 where type='icd'
# 79,866,333
## Number of lab records:
# select count(*) from p2v_all_patients_events_combined_2 where type='lab'
# 216,392,248
## Number of med records:
# select count(*) from p2v_all_patients_events_combined_2 where type='med'
# 66,269,824

## Distinct codes ('words'):
# select count(distinct code) from p2v_all_patients_events_combined_2
# 31,543 / 31,589
## Distinct ICD-9 codes
# select count(distinct code) from p2v_all_patients_events_combined_2 where type='icd'
# 19,994
## Distinct lab codes
# select count(distinct code) from p2v_all_patients_events_combined_2 where type='lab'
# 5,509
## Distinct med codes
# select count(distinct code) from p2v_all_patients_events_combined_2 where type='med'
# 6,086

## Number of patients:
# select count(distinct ind_seq) from p2v_all_patients_events_combined_2;
# 2,309,712

# 'embedding_stats.csv' file
# select ind_seq, months_between(max(entry_date), min(entry_date)),
# count(*) as total_count,
# sum(case type when 'med' then 1 else 0 end) as med_count,
# sum(case type when 'lab' then 1 else 0 end) as lab_count,
# sum(case type when 'icd' then 1 else 0 end) as icd_count
# from p2v_all_patients_events_combined_2 group by ind_seq;


import numpy as np
import pandas as pd
from tqdm import *

STATS_FILE = 'embedding_stats.csv'
stats_df = pd.read_csv(STATS_FILE, index_col=None)

## Per patient
for c in ['MONTHS_BETWEEN', 'TOTAL_COUNT', 'MED_COUNT', 'LAB_COUNT', 'ICD_COUNT']:
    print("{}:\t{:.1f} [{:.1f}, {:.1f}]".format(c, stats_df[c].median(), stats_df[c].quantile(0.25), stats_df[c].quantile(0.75)))

# MONTHS_BETWEEN:	11.8 [0, 67.3]
# TOTAL_COUNT:	21 [4, 93]
# MED_COUNT:	2 [0, 14]
# LAB_COUNT:	1 [0, 49]
# ICD_COUNT:	8 [3, 27]
