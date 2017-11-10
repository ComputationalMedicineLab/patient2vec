-------------------------------------------------------------------------------
-- TABLE p2v_patients_outcome
-------------------------------------------------------------------------------
-- Contains ids of patients chosen for the experiment with code cutoff date and
-- outcome.
-- Columns:
--  - cutoff_date - cutoff date for data
--  - ind_seq
--  - outcome (1 - has diabetes medication, 0 - no diabetes medication)
-------------------------------------------------------------------------------

CREATE TABLE p2v_patients_outcome (
    CUTOFF_DATE varchar(255),
    IND_SEQ int,
    OUTCOME int,
    T_GROUP varchar(63)
);

INSERT INTO p2v_patients_outcome
SELECT * FROM
  EXTERNAL '<PATH_TO_THE_PROJECT>/patient2vec/data/intermediate/patient_list_split.csv'
USING
(
 DELIMITER ','
 LOGDIR '<PATH_TO_THE_PROJECT>/patient2vec/log'
 SKIPROWS 1
 Y2BASE 2000
 ENCODING 'internal'
 REMOTESOURCE 'JDBC' -- alternative is 'ODBC'
 ESCAPECHAR '\'
 QUOTEDVALUE 'DOUBLE'
)


-------------------------------------------------------------------------------
-- TABLE p2v_diabetes_all_patients_events
-------------------------------------------------------------------------------
-- Contains all codes (ICD-9/medication/lab) for patients selected for
-- the experiment (table p2v_patients_outcome) before cutoff date.
-- Columns:
--  - ind_seq
--  - entry_date
--  - code (ICD-9/medication/lab)
-------------------------------------------------------------------------------

CREATE TABLE p2v_diabetes_all_patients_events AS
(
  (
    SELECT DISTINCT ind_seq, entry_date, code, 'icd' as type FROM
    (
      SELECT codes.ind_seq, codes.entry_date, codes.code, outcome.cutoff_date FROM
        (
          SELECT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, code FROM icd_codes
          WHERE ind_seq IN (SELECT DISTINCT ind_seq FROM p2v_patients_outcome)
          ORDER BY ind_seq, entry_date
        ) as codes
      LEFT JOIN
        (SELECT ind_seq, cutoff_date FROM p2v_patients_outcome) AS outcome
      ON codes.ind_seq = outcome.ind_seq
    ) as codes_d
    WHERE codes_d.entry_date < codes_d.cutoff_date
  )
  UNION ALL
  (
    SELECT DISTINCT ind_seq, entry_date, test_sname as code, 'lab' as type FROM
    (
      SELECT labs.ind_seq, labs.entry_date, labs.test_sname, outcome.cutoff_date FROM
        (
          SELECT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, test_sname FROM labs_num
          WHERE ind_seq IN (SELECT DISTINCT ind_seq FROM p2v_patients_outcome)
          ORDER BY ind_seq, entry_date
        ) as labs
      LEFT JOIN
        (SELECT ind_seq, cutoff_date FROM p2v_patients_outcome) AS outcome
      ON labs.ind_seq = outcome.ind_seq
    ) as labs_d
    WHERE labs_d.entry_date < labs_d.cutoff_date
  )
  UNION ALL
  (
    SELECT DISTINCT ind_seq, entry_date, generic_name as code, 'med' as type FROM
    (
      SELECT meds.ind_seq, meds.entry_date, meds.generic_name, outcome.cutoff_date FROM
        (
          SELECT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, generic_name FROM medex
          WHERE ind_seq IN (SELECT DISTINCT ind_seq FROM p2v_patients_outcome)
          AND drug_strength <> '' AND drug_strength IS NOT NULL AND route <> ''
          AND route IS NOT NULL AND drug_freq <> '' AND drug_freq IS NOT NULL
          AND generic_name IS NOT NULL AND generic_name <> ''
          ORDER BY ind_seq, entry_date
        ) as meds
      LEFT JOIN
        (SELECT ind_seq, cutoff_date FROM p2v_patients_outcome) AS outcome
      ON meds.ind_seq = outcome.ind_seq
    ) as meds_d
    WHERE meds_d.entry_date < meds_d.cutoff_date
  )
  ORDER BY ind_seq, entry_date
);

-- data/raw/diabetes_patients_codes.csv
SELECT * FROM p2v_diabetes_all_patients_events;
