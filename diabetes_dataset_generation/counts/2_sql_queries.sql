-------------------------------------------------------------------------------
-- TABLE p2v_rxcui_atc_map
-------------------------------------------------------------------------------
-- RXCUID to ATC mapping
-- Columns:
--  - RXCUID
--  - GENERIC_RXCUID
--  - ATC_CLASS
--  - ATC_DESC - description of the ATC class
-------------------------------------------------------------------------------

CREATE TABLE p2v_rxcui_atc_map (
    rxcuid varchar(15),
    generic_rxcuid varchar(15),
    atc_class varchar(63),
    atc_desc varchar(255)
);

INSERT INTO p2v_rxcui_atc_map
SELECT * FROM
  EXTERNAL '<PATH_TO_THE_PROJECT>/patient2vec/data/intermediate/rxcui_atc_map.csv'
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
-- TABLE p2v_rxcui_atc_map
-------------------------------------------------------------------------------
-- Generic drug name to ATC mapping (for drugs in
-- p2v_diabetes_all_patients_events table)
-- Columns:
--  - generic_name
--  - generic_rxnorm_id
--  - atc_class
-------------------------------------------------------------------------------
CREATE TABLE p2v_diabetes_meds_atc_map AS
(
  SELECT DISTINCT lower(medex.generic_name) as generic_name, medex.generic_rxnorm_id, p2v_rxcui_atc_map.atc_class
  FROM medex
  JOIN p2v_rxcui_atc_map ON medex.generic_rxnorm_id = p2v_rxcui_atc_map.generic_rxcuid
  WHERE lower(medex.generic_name) in
  	(SELECT DISTINCT code FROM p2v_diabetes_all_patients_events WHERE type = 'med')
)

-- data/intermediate/generic_name_atc_map.csv
SELECT * FROM p2v_diabetes_meds_atc_map ORDER BY generic_name;

-- data/intermediate/icd_phewas_map.csv
SELECT * FROM icd_phewas_map ORDER BY icd_code;
