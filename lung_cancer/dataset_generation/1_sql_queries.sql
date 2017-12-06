-------------------------------------------------------------------------------
-- TABLE p2v_lung_cancer_biopsy_temp
-------------------------------------------------------------------------------
-- Contains list of patients that have a record of a lung biopsy.
-- Criteria include:
--  - Patient has at least one ICD-9 code from 33.2 group (Diagnostic
--    Procedures On Lung And Bronchus) or
--  - Patient has a least one CPT code for lung biopsy ('31628','31632',
--    '32095','32096','32097','32405','32601','32602','32607','32608')
-- Columns:
--  - ind_seq
--  - biopsy_count - number of biopsy records
--  - first_biopsy - date of the first biopsy
-------------------------------------------------------------------------------
CREATE TABLE p2v_lung_cancer_biopsy_temp AS
(
	SELECT ind_seq, SUM(biopsy_count) AS biopsy_count, MIN(first_biopsy) AS first_biopsy FROM
	(
		SELECT ind_seq, count(*) AS biopsy_count, TO_CHAR(MIN(entry_date), 'YYYY-MM-DD') AS first_biopsy FROM icd_codes WHERE code LIKE '33.2%' GROUP BY ind_seq
		UNION ALL
		SELECT ind_seq, count(*) AS biopsy_count, TO_CHAR(MIN(entry_date), 'YYYY-MM-DD') AS first_biopsy FROM cpt_codes WHERE code IN ('31628','31632','32095','32096','32097','32405','32601','32602','32607','32608') GROUP BY ind_seq
	) AS combined_icd_cpt_biopsy
	GROUP BY ind_seq
	ORDER BY ind_seq
)

-------------------------------------------------------------------------------
-- TABLE p2v_lung_cancer_biopsy_patients_temp
-------------------------------------------------------------------------------
-- Contains list of patients that have a record of a lung biopsy and have
-- enough records for the experiment.
-- Criteria include:
--  - Patient is in p2v_lung_cancer_biopsy_temp table (see details above)
--  - Patient has at least 10 ICD-9 codes before the first biopsy
--  - Patient has at least 24 months of history before the first biopsy
--  - Patient has less than 500 months of history before the first biopsy
--    (more than 500 indicate an error in records)
-- Columns:
--  - ind_seq
--  - first_icd_code - date of the first ICD-9 code
--  - first_biopsy - date of the first lung biopsy
--  - biopsy_count - number of biopsy records
--  - codes_before - number of ICD-9 codes before the first biopsy
--  - months_codes_before - months of records before the first biopsy
-------------------------------------------------------------------------------
CREATE TABLE p2v_lung_cancer_biopsy_patients_temp AS
(
	SELECT * FROM
	(
		SELECT ind_seq, MIN(entry_date) AS first_icd_code, MIN(first_biopsy) AS first_biopsy, MIN(biopsy_count) AS biopsy_count, COUNT(*) AS codes_before, months_between(MIN(first_biopsy), MIN(entry_date)) AS months_codes_before FROM
		(
			SELECT icd_codes.ind_seq, TO_CHAR(icd_codes.entry_date, 'YYYY-MM-DD') AS entry_date, p2v_lung_cancer_biopsy_temp.first_biopsy, p2v_lung_cancer_biopsy_temp.biopsy_count FROM icd_codes
			INNER JOIN p2v_lung_cancer_biopsy_temp ON p2v_lung_cancer_biopsy_temp.ind_seq = icd_codes.ind_seq
			WHERE icd_codes.ind_seq IN (SELECT DISTINCT ind_seq from p2v_lung_cancer_biopsy_temp)
			AND entry_date < p2v_lung_cancer_biopsy_temp.first_biopsy
		) AS biopsy_counts
		GROUP BY ind_seq
	) AS biopsy
	WHERE months_codes_before >= 24
	AND months_codes_before < 500
	AND codes_before >= 10
	ORDER BY ind_seq
)

-------------------------------------------------------------------------------
-- TABLE p2v_lung_cancer_biopsy_patients_with_cancer_temp
-------------------------------------------------------------------------------
-- Contains list of patients that have a record of a lung biopsy, have
-- enough records for the experiment and had lung cancer diagnosis ICD-9 code.
-- Criteria include:
--  - Patients is in p2v_lung_cancer_biopsy_patients_temp table (see details
--    above)
--  - Patient has at least one occurrence of 162.* ICD-9 code (Malignant
--    neoplasm of trachea bronchus and lung)
-- Columns:
--  - ind_seq
--  - lung_cancer_count - number of 162.* records
--  - first_lung_cancer - date of the first 162.* record
--  - first_biopsy - date of the first lung biopsy
--  - months_between - months between first_biopsy and first_lung_cancer
--  - codes_before - number of ICD-9 codes before the first biopsy
--  - months_codes_before - months of records before the first biopsy
-------------------------------------------------------------------------------
CREATE TABLE p2v_lung_cancer_biopsy_patients_with_cancer_temp AS
(
	SELECT icd_codes.ind_seq, COUNT(*) AS lung_cancer_count, TO_CHAR(MIN(icd_codes.entry_date), 'YYYY-MM-DD') AS first_lung_cancer, MIN(p2v_lung_cancer_biopsy_patients_temp.first_biopsy) AS first_biopsy, months_between(TO_CHAR(MIN(icd_codes.entry_date), 'YYYY-MM-DD'), MIN(p2v_lung_cancer_biopsy_patients_temp.first_biopsy)), MIN(p2v_lung_cancer_biopsy_patients_temp.codes_before) AS codes_before, MIN(p2v_lung_cancer_biopsy_patients_temp.months_codes_before) AS months_codes_before FROM icd_codes
	LEFT JOIN p2v_lung_cancer_biopsy_patients_temp ON p2v_lung_cancer_biopsy_patients_temp.ind_seq = icd_codes.ind_seq
	WHERE parent = '162'
	AND icd_codes.ind_seq IN (SELECT DISTINCT ind_seq from p2v_lung_cancer_biopsy_patients_temp)
	GROUP BY icd_codes.ind_seq
	ORDER BY icd_codes.ind_seq
)


-- List of patients with lung cancer diagnosed after lung biopsy (months_between >= 0)
-- lung_cancer/data/raw/lung_biopsy_cancer.csv
SELECT * FROM p2v_lung_cancer_biopsy_patients_with_cancer_temp WHERE months_between >= 0
-- 1,185 rows

-- List of patients with lung biopsy, but no lung cancer
-- lung_cancer/data/raw/lung_biopsy_cancer_control.csv
SELECT * FROM p2v_lung_cancer_biopsy_patients_temp
WHERE ind_seq NOT IN (SELECT DISTINCT ind_seq FROM icd_codes WHERE parent = '162')
-- 5,631 rows
