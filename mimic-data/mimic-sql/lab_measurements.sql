-- Export this query to "mimic_lab_measurements.csv"
WITH
aptt_measurements AS (
  SELECT subject_id, charttime AS timestamp, valuenum AS aPTT FROM mimiciii.labevents WHERE itemid = '51275' AND valuenum IS NOT NULL
),
heparin_bolus_injections AS (
  SELECT subject_id, endtime AS timestamp, amount AS heparin_dose_bolus FROM mimiciii.inputevents_mv WHERE itemid = '225152' AND amount IS NOT NULL AND statusdescription != 'Rewritten' AND rate IS NULL
),
pt_measurements AS (
  SELECT subject_id, charttime AS timestamp, valuenum AS prothrombin_time FROM mimiciii.labevents WHERE itemid = '51237' AND valuenum IS NOT NULL
),
platelet_counts AS (
  SELECT subject_id, charttime AS timestamp, valuenum AS platelet_count FROM mimiciii.labevents WHERE itemid = '51265' AND valuenum IS NOT NULL
),
hemoglobin_measurements AS (
  -- http://www.scymed.com/en/smnxpf/pfxdq210_c.htm
  -- Convert g/dL to mmol/L
  SELECT subject_id, charttime AS timestamp, ROUND(CAST((valuenum * 0.6206) AS NUMERIC), 1)  AS hemoglobin FROM mimiciii.labevents WHERE itemid = '51222' AND valuenum IS NOT NULL
),
hematocrit_measurements AS (
  SELECT subject_id, charttime AS timestamp, (valuenum / 100) AS hematocrit FROM mimiciii.labevents WHERE itemid = '51221' AND valuenum IS NOT NULL
),
bilirubin_measurements AS (
  -- http://www.scymed.com/en/smnxtb/tbcbbqr1.htm
  -- Convert mg/dL to umol/L
  SELECT subject_id, charttime AS timestamp, ROUND(CAST((valuenum * 17.1) AS NUMERIC), 1) AS bilirubin FROM mimiciii.labevents WHERE itemid = '50885' AND valuenum IS NOT NULL
),
creatinine_measurements AS (
  -- http://www.scymed.com/en/smnxtb/tbcbdnc1.htm
  -- Convert mg/dL to umol/L
  SELECT subject_id, charttime AS timestamp, ROUND(CAST((valuenum * 88.42) AS NUMERIC), 1) AS creatinine FROM mimiciii.labevents WHERE itemid = '50912' AND valuenum IS NOT NULL
)
SELECT
  rs.subject_id AS patient_id,
  aptt_prev.timestamp AS ts_aptt_prev,
  aptt_prev.aPTT AS aptt_prev,
  rs.starttime AS ts_infusion,
  ROUND(CAST(rs.originalrate AS NUMERIC), 1) AS heparin_dose,
  (CASE WHEN bolus.heparin_dose_bolus IS NULL THEN 0 ELSE 1 END) AS is_bolus,
  bolus.heparin_dose_bolus AS heparin_dose_bolus,
  aptt_next.timestamp AS ts_aptt_next,
  aptt_next.aPTT AS aptt_next,
  ROUND(CAST(EXTRACT(EPOCH FROM aptt_next.timestamp - rs.starttime) / 60 AS NUMERIC), 1) AS aptt_interval,
  pt.prothrombin_time AS prothrombin_time,
  pt.timestamp AS ts_prothrombin_time,
  plat.platelet_count AS platelet_count,
  plat.timestamp AS ts_platelet_count,
  hb.hemoglobin AS hemoglobin,
  hb.timestamp AS ts_hemoglobin,
  ht.hematocrit AS hematocrit,
  ht.timestamp AS ts_hematocrit,
  br.bilirubin AS bilirubin,
  br.timestamp AS ts_bilirubin,
  cr.creatinine AS creatinine,
  cr.timestamp AS ts_creatinine
FROM mimiciii.inputevents_mv rs
LEFT JOIN
  aptt_measurements aptt_prev ON (
    (rs.subject_id = aptt_prev.subject_id)
    AND
    -- aPTT measurements 4 hours before the initial infusion. -> aPTT_prev
    (aptt_prev.timestamp BETWEEN (rs.starttime - INTERVAL '4 HOURS') AND rs.starttime)
  )
LEFT JOIN
  aptt_measurements aptt_next ON (
    (rs.subject_id = aptt_next.subject_id)
    AND
    -- aPTT measurements 4-8 hours after the initial infusion. -> aPTT_next
    (aptt_next.timestamp BETWEEN (rs.starttime + INTERVAL '4 HOURS') AND (rs.starttime + INTERVAL '8 HOURS'))
    AND
    -- Next aPTT measurement taken while infusion still goes on.
    aptt_next.timestamp < rs.endtime
  )
LEFT JOIN
  heparin_bolus_injections bolus ON (
    (rs.subject_id = bolus.subject_id)
    AND
    -- Bolus injection +- 5 minutes from infusion start.
    (bolus.timestamp BETWEEN (rs.starttime - INTERVAL '5 MINUTES') AND (rs.starttime + INTERVAL '5 MINUTES'))
  )
LEFT JOIN
  pt_measurements pt ON (
    (rs.subject_id = pt.subject_id)
    AND
    -- PT measurements close to aPTT measurement.
    (pt.timestamp BETWEEN (aptt_prev.timestamp - INTERVAL '2 HOURS') AND (aptt_prev.timestamp + INTERVAL '2 HOURS'))
  )
LEFT JOIN
  platelet_counts plat ON (
    (rs.subject_id = plat.subject_id)
    AND
    -- Platelet count measurement close to aPTT measurement.
    (plat.timestamp BETWEEN (aptt_prev.timestamp - INTERVAL '2 HOURS') AND (aptt_prev.timestamp + INTERVAL '2 HOURS'))
  )
LEFT JOIN
  hemoglobin_measurements hb ON (
    (rs.subject_id = hb.subject_id)
    AND
    -- Hemoglobin measurement close to aPTT measurement.
    (hb.timestamp BETWEEN (aptt_prev.timestamp - INTERVAL '2 HOURS') AND (aptt_prev.timestamp + INTERVAL '2 HOURS'))
  )
LEFT JOIN
  hematocrit_measurements ht ON (
    (rs.subject_id = ht.subject_id)
    AND
    -- Hematocrit measurement close to aPTT measurement.
    (ht.timestamp BETWEEN (aptt_prev.timestamp - INTERVAL '2 HOURS') AND (aptt_prev.timestamp + INTERVAL '2 HOURS'))
  )
LEFT JOIN
  bilirubin_measurements br ON (
    (rs.subject_id = br.subject_id)
    AND
    -- Bilirubin measurement close to aPTT measurement. (ALLOWED NULLS because we propagate 1 day forward later)
    (br.timestamp BETWEEN (aptt_prev.timestamp - INTERVAL '2 HOURS') AND (aptt_prev.timestamp + INTERVAL '2 HOURS'))
  )
LEFT JOIN
  creatinine_measurements cr ON (
    (rs.subject_id = cr.subject_id)
    AND
    -- Creatinine measurement close to aPTT measurement. (ALLOWED NULLS because we propagate 1 day forward later)
    (cr.timestamp BETWEEN (aptt_prev.timestamp - INTERVAL '2 HOURS') AND (aptt_prev.timestamp + INTERVAL '2 HOURS'))
  )
WHERE
  rs.itemid = '225152'
  AND
  rs.statusdescription != 'Rewritten'
  AND
  rs.rate IS NOT NULL -- No injections.
  AND
  aptt_prev.aPTT IS NOT NULL
  AND
  aptt_next.aPTT IS NOT NULL
  AND
  pt.prothrombin_time IS NOT NULL
  AND
  plat.platelet_count IS NOT NULL
  AND
  hb.hemoglobin IS NOT NULL
  AND
  ht.hematocrit IS NOT NULL
ORDER BY rs.subject_id ASC, rs.starttime ASC
;
