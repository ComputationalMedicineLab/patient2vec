-------------------------------------------------------------------------------
-- TABLE p2v_diabetes_drug_patients
-------------------------------------------------------------------------------
-- Contains list of patients matching criteria for type 2 diabates.
-- Criteria include:
--  - Patient has more than 10 complete records of medication from ATC group
--    A10B (BLOOD GLUCOSE LOWERING DRUGS, EXCL. INSULINS) (generic_rxnorm_id
--    or rxnorm_id in (...))
--  - Full record of medication includes drug_strength, route and drug_freq
--  - Patient has a least 10 ICD-9 recorded before the first occurrence of
--    a A10B medication ('distinct' by day)
--  - Patient has a least 24 months of recorded history before the first
--    occurrence of a A10B medication
--  - Patient has a less than 500 months of recorded history before the first
--    occurrence of a A10B medication (more than 500 indicate an error in records)
--  - Patient has no complete record of any medication from ATC group A10
--    (DRUGS USED IN DIABETS) before first complete record of A10B medication
-- Columns:
--  - ind_seq
--  - first_diabetes_drug - date of the first complete record of diabetes med.
--  - count_diabetes_drug - number of complete records of diabetes med.
--  - count_codes_before_drug - number of ICD-9 codes before
--    first_diabetes_drug date (< first_diabetes_drug)
--  - months_codes_before_drug - number of months between the first patient's
--    ICD-9 code and first_diabetes_drug
-------------------------------------------------------------------------------

CREATE TABLE p2v_diabetes_drug_patients AS
(
  SELECT * FROM
  (
    SELECT ind_seq, MIN(first_diabetes_drug) AS first_diabetes_drug, MIN(count_diabetes_drug) AS count_diabetes_drug, COUNT(*) AS count_codes_before_drug, months_between(MIN(first_diabetes_drug), MIN(entry_date)) as months_codes_before_drug FROM
    (
      SELECT ind_seq, first_diabetes_drug, code, entry_date, count_diabetes_drug FROM
      (
        SELECT drug.ind_seq, drug.first_diabetes_drug, icd.code, icd.entry_date, drug.count_diabetes_drug FROM
          (
            SELECT ind_seq, TO_CHAR(MIN(entry_date), 'YYYY-MM-DD') AS first_diabetes_drug, COUNT(*) AS count_diabetes_drug FROM medex
            WHERE
              (
                rxnorm_id in ('173','2068','2404','4815','4816','4821','6809','8129','10633','10635','16681','18880','25789','25793','26344','30009','33738','60548','72610','73044','84108','102846','102848','139953','274332','475968','593411','596554','606253','607999','614348','647235','729717','802646','857974','1043562','1100699','1189803','1243019','1368001','1368384','1368402','1373458','1440051','1486436','1488564','1534763','1545149','1545653','1551291','1598392','1664314','1727500')
                OR
                generic_rxnorm_id in ('173','2068','2404','4815','4816','4821','6809','8129','10633','10635','16681','18880','25789','25793','26344','30009','33738','60548','72610','73044','84108','102846','102848','139953','274332','475968','593411','596554','606253','607999','614348','647235','729717','802646','857974','1043562','1100699','1189803','1243019','1368001','1368384','1368402','1373458','1440051','1486436','1488564','1534763','1545149','1545653','1551291','1598392','1664314','1727500')
              )
            AND drug_strength <> '' AND drug_strength IS NOT NULL AND route <> '' AND route IS NOT NULL AND drug_freq <> '' AND drug_freq IS NOT NULL
            GROUP BY ind_seq
          ) AS drug
        LEFT JOIN
          (SELECT DISTINCT ind_seq, TO_CHAR(entry_date, 'YYYY-MM-DD') as entry_date, code FROM icd_codes) AS icd
        ON drug.ind_seq = icd.ind_seq
      ) as drug_and_codes
      WHERE drug_and_codes.entry_date < drug_and_codes.first_diabetes_drug
      ORDER BY ind_seq, entry_date asc
    ) as drug_and_codes_before_drugs
    GROUP BY drug_and_codes_before_drugs.ind_seq
  ) as patients
  WHERE count_diabetes_drug > 10
  AND count_codes_before_drug >= 10
  AND months_codes_before_drug >= 24
  AND months_codes_before_drug < 500
  AND ind_seq NOT IN
  (
    SELECT distinct ind_seq FROM
      (
      SELECT drug.ind_seq, drug.first_diabetes_drug, drug.count_diabetes_drug, diabetes_drugs.drug_name, diabetes_drugs.entry_date FROM
        (
          SELECT ind_seq, TO_CHAR(MIN(entry_date), 'YYYY-MM-DD') AS first_diabetes_drug, COUNT(*) AS count_diabetes_drug FROM medex
          WHERE
            (
              (
                rxnorm_id in ('173','2068','2404','4815','4816','4821','6809','8129','10633','10635','16681','18880','25789','25793','26344','30009','33738','60548','72610','73044','84108','102846','102848','139953','274332','475968','593411','596554','606253','607999','614348','647235','729717','802646','857974','1043562','1100699','1189803','1243019','1368001','1368384','1368402','1373458','1440051','1486436','1488564','1534763','1545149','1545653','1551291','1598392','1664314','1727500')
                OR
                generic_rxnorm_id in ('173','2068','2404','4815','4816','4821','6809','8129','10633','10635','16681','18880','25789','25793','26344','30009','33738','60548','72610','73044','84108','102846','102848','139953','274332','475968','593411','596554','606253','607999','614348','647235','729717','802646','857974','1043562','1100699','1189803','1243019','1368001','1368384','1368402','1373458','1440051','1486436','1488564','1534763','1545149','1545653','1551291','1598392','1664314','1727500')
              )
              AND drug_strength <> '' AND drug_strength IS NOT NULL AND route <> '' AND route IS NOT NULL AND drug_freq <> '' AND drug_freq IS NOT NULL
            )
          GROUP BY ind_seq
        ) AS drug
      LEFT JOIN
        (
          SELECT DISTINCT ind_seq, TO_CHAR(entry_date, 'YYYY-MM-DD') as entry_date, drug_name FROM medex
          WHERE
            (
              rxnorm_id IN ('173','2068','2404','4815','4816','4821','6809','8129','10633','10635','16681','18880','25789','25793','26344','30009','33738','38386','60548','72610','73044','84108','86009','102846','102848','139825','139953','253182','274332','274783','400008','475968','593411','596554','606253','607999','614348','647235','729717','802646','857974','1043562','1100699','1189803','1243019','1309342','1368001','1368384','1368402','1373458','1440051','1486436','1488564','1534763','1545149','1545653','1551291','1598392','1664314','1670007','1727493','1727500')
              OR generic_rxnorm_id IN ('173','2068','2404','4815','4816','4821','6809','8129','10633','10635','16681','18880','25789','25793','26344','30009','33738','38386','60548','72610','73044','84108','86009','102846','102848','139825','139953','253182','274332','274783','400008','475968','593411','596554','606253','607999','614348','647235','729717','802646','857974','1043562','1100699','1189803','1243019','1309342','1368001','1368384','1368402','1373458','1440051','1486436','1488564','1534763','1545149','1545653','1551291','1598392','1664314','1670007','1727493','1727500')
            )
            AND drug_strength <> '' AND drug_strength IS NOT NULL AND route <> '' AND route IS NOT NULL AND drug_freq <> '' AND drug_freq IS NOT NULL
        ) AS diabetes_drugs
      ON drug.ind_seq = diabetes_drugs.ind_seq
    ) as combined_diabetes_drugs
    WHERE entry_date < first_diabetes_drug
  )
  ORDER BY ind_seq
);

-- diabetes/data/raw/diabetes_drug.csv
SELECT * FROM p2v_diabetes_drug_patients; -- 10,477 rows

-------------------------------------------------------------------------------
-- TABLE p2v_diabetes_drug_controls
-------------------------------------------------------------------------------
-- Contains list of patients matching criteria for type 2 diabates control
-- Criteria include:
--  - Patient has no mention of any medication from ATC group A10
--    (DRUGS USED IN DIABETES) (generic_rxnorm_id or rxnorm_id in (...))
--  - Patient has a least 10 ICD-9 recorded ('distinct' by day)
--  - Patient has a least 24 months of recorded history
--  - Patient has less than 500 months of recorded history
--    (more than 500 indicate an error in records)
-- Columns:
--  - ind_seq
--  - count_codes - number of ICD-9
--  - months_codes - number of months between the first and last ICD-9 code
-------------------------------------------------------------------------------

CREATE TABLE p2v_diabetes_drug_controls AS
(
  SELECT * FROM
  (
    SELECT ind_seq, COUNT(*) AS count_codes, months_between(MAX(entry_date), MIN(entry_date)) AS months_codes FROM
    (
    	SELECT distinct ind_seq, code, entry_date FROM icd_codes
    	WHERE
    	ind_seq NOT IN
    		(
          SELECT DISTINCT ind_seq FROM medex
          WHERE rxnorm_id IN ('16681', '173', '1534763', '1368001', '1368384', '1368402', '18880', '1373458', '1545149', '2068', '2404', '1488564', '1486436', '1727500', '1551291', '1545653', '1598392', '1664314', '60548', '102846', '4816', '25789', '647235', '606253', '4821', '25793', '4815', '102848', '26344', '1670007', '1727493', '139825', '274783', '86009', '400008', '1309342', '1100699', '1243019', '475968', '1440051', '6809', '607999', '802646', '614348', '1043562', '729717', '30009', '274332', '8129', '33738', '139953', '253182', '73044', '84108', '857974', '1189803', '593411', '10633', '10635', '38386', '72610', '596554')
          OR generic_rxnorm_id IN ('16681', '173', '1534763', '1368001', '1368384', '1368402', '18880', '1373458', '1545149', '2068', '2404', '1488564', '1486436', '1727500', '1551291', '1545653', '1598392', '1664314', '60548', '102846', '4816', '25789', '647235', '606253', '4821', '25793', '4815', '102848', '26344', '1670007', '1727493', '139825', '274783', '86009', '400008', '1309342', '1100699', '1243019', '475968', '1440051', '6809', '607999', '802646', '614348', '1043562', '729717', '30009', '274332', '8129', '33738', '139953', '253182', '73044', '84108', '857974', '1189803', '593411', '10633', '10635', '38386', '72610', '596554')
        )
    ) AS codes
    GROUP BY ind_seq
  ) as patients
  WHERE count_codes >= 10 AND months_codes >= 24 AND months_codes < 500
  ORDER BY ind_seq
);

-- data/raw/diabetes_drug_control.csv
SELECT * FROM p2v_diabetes_drug_controls; -- 528,068 rows
