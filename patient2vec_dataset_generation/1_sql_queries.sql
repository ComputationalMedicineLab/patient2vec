CREATE TABLE p2v_all_patients_events_combined AS
(
  (SELECT DISTINCT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, code FROM icd_codes)
  UNION ALL
  (SELECT DISTINCT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, test_sname AS code FROM labs_num)
  UNION ALL
  (
    SELECT DISTINCT ind_seq, to_char(entry_date, 'YYYY-MM-DD') AS entry_date, generic_name AS code FROM medex
      WHERE drug_strength <> '' AND drug_strength IS NOT NULL AND route <> ''
      AND route IS NOT NULL AND drug_freq <> '' AND drug_freq IS NOT NULL
      AND generic_name IS NOT NULL AND generic_name <> ''
  )
  ORDER BY ind_seq, entry_date
);

-- data/raw/all_patients_events_combined.csv
select * from p2v_all_patients_events_combined;
