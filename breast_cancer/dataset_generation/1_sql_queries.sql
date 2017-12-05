-------------------------------------------------------------------------------
-- TABLE p2v_breast_cancer_patients
-------------------------------------------------------------------------------
-- Contains list of patients matching criteria for breast cancer.
-- Criteria include:
--  - Patient at least 3 ICD-9 codes from 174 group (Malignant neoplasm of
--    female breast)
--  - Patient has a least 10 ICD-9 recorded before the first occurrence of
--    code from 174 group
--  - Patient has a least 24 months of recorded history before the first
--    occurrence of a 174.* code
--  - Patient has a less than 500 months of recorded history before the first
--    occurrence of of a 174.* code
-- Columns:
--  - ind_seq
--  - first_breast_cancer - date of the first occurrence of a 174.* code
--  - count_breast_cancer - number of 174.* code occurrences
--  - count_codes_before - number of ICD-9 codes before first_breast_cancer
--    date (< first_breast_cancer)
--  - months_codes_before - number of months between the first patient's
--    ICD-9 code and first_breast_cancer
-------------------------------------------------------------------------------

CREATE TABLE p2v_breast_cancer_patients AS
(
  SELECT * FROM
  (
  	SELECT ind_seq, MIN(first_breast_cancer) AS first_breast_cancer, MIN(count_breast_cancer) AS count_breast_cancer, COUNT(*) AS count_codes_before, months_between(MIN(first_breast_cancer), MIN(entry_date)) as months_codes_before FROM
  	(
  		SELECT ind_seq, first_breast_cancer, code, entry_date, count_breast_cancer FROM
  		(
  			SELECT bc_code.ind_seq, bc_code.first_breast_cancer, icd.code, icd.entry_date, bc_code.count_breast_cancer FROM
  			(
  		    SELECT ind_seq, TO_CHAR(MIN(entry_date), 'YYYY-MM-DD') AS first_breast_cancer, count(*) as count_breast_cancer FROM icd_codes
  				WHERE code LIKE '174%'
  				GROUP BY ind_seq
  		  ) AS bc_code
  		  LEFT JOIN
  		   	(SELECT DISTINCT ind_seq, TO_CHAR(entry_date, 'YYYY-MM-DD') as entry_date, code FROM icd_codes) AS icd
  		  ON bc_code.ind_seq = icd.ind_seq
  		) AS bc_and_codes
  		WHERE bc_and_codes.entry_date < bc_and_codes.first_breast_cancer
  		ORDER BY ind_seq, entry_date asc
  	) AS combined
  	GROUP BY combined.ind_seq
  ) AS foo
  WHERE months_codes_before >= 24
  AND months_codes_before < 500
  AND count_codes_before >= 10
  AND count_breast_cancer >= 3
  ORDER BY ind_seq
);

-- breast_cancer/data/raw/breast_cancer.csv
SELECT * FROM p2v_breast_cancer_patients; -- 2,901 rows

-------------------------------------------------------------------------------
-- TABLE p2v_breast_cancer_controls
-------------------------------------------------------------------------------
-- Contains list of patients matching criteria for breast cancer control
-- Criteria include:
--  - Patient has no ICD-9 codes from 174 group (Malignant neoplasm of female
--    breast)
--  - Patient is female
--  - Patient has a least 10 ICD-9 recorded ('distinct' by day)
--  - Patient has a least 12 months of recorded history
--  - Patient has less than 500 months of recorded history
--    (more than 500 indicate an error in records)
-- Columns:
--  - ind_seq
--  - count_codes - number of ICD-9
--  - months_codes - number of months between the first and last ICD-9 code
-------------------------------------------------------------------------------

CREATE TABLE p2v_breast_cancer_controls AS
(
  SELECT * FROM
  (
    SELECT ind_seq, COUNT(*) AS count_codes, months_between(MAX(entry_date), MIN(entry_date)) AS months_codes FROM
    (
    	SELECT distinct ind_seq, code, entry_date FROM icd_codes
    	WHERE ind_seq NOT IN (SELECT DISTINCT ind_seq FROM icd_codes WHERE code LIKE '174%')
    	AND ind_seq IN (SELECT ind_seq FROM sd_record WHERE gender_epic='F')
    ) AS codes
    GROUP BY ind_seq
  ) as patients
  WHERE count_codes >= 10 AND months_codes >= 24 AND months_codes < 500
  ORDER BY ind_seq
);

-- breast_cancer/data/raw/breast_cancer_control.csv
SELECT * FROM p2v_breast_cancer_controls; -- 391,137 rows
