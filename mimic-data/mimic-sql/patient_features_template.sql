-- Export this query to "mimic_patient_featrures.csv"
WITH
patient_weight AS (
  SELECT
    e.subject_id AS patient_id,
    MAX(e.valuenum) AS weight
  FROM
    mimiciii.chartevents e
  WHERE
    e.subject_id IN %REPLACE%
    AND
    e.itemid = 224639
  GROUP BY e.subject_id
),
patient_height AS (
  SELECT
    e.subject_id AS patient_id,
    MAX(e.valuenum) AS height
  FROM
    mimiciii.chartevents e
  WHERE
    e.subject_id IN %REPLACE%
    AND
    e.itemid = 226730
  GROUP BY e.subject_id
),
patient_gender AS (
  SELECT
    pa.subject_id AS patient_id,
    CASE WHEN pa.gender='M' THEN 0 WHEN pa.gender='F' THEN 1 END AS gender
  FROM
    mimiciii.patients pa
  WHERE
    pa.subject_id IN %REPLACE%
),
patient_age AS (
  SELECT
    pa.subject_id AS patient_id,
    date_part('year', (SELECT storetime FROM mimiciii.inputevents_mv e WHERE e.subject_id = pa.subject_id ORDER BY storetime ASC LIMIT 1)) - date_part('year', pa.dob) AS age
  FROM
    mimiciii.patients pa
  WHERE
    pa.subject_id IN %REPLACE%
)
SELECT
  w.patient_id,
  w.weight,
  h.height,
  g.gender,
  a.age,
  ROUND(CAST(w.weight / POWER((h.height / 100), 2) AS NUMERIC), 1) AS bmi
FROM patient_weight w
  INNER JOIN patient_height h ON w.patient_id = h.patient_id
  INNER JOIN patient_gender g ON w.patient_id = g.patient_id
  INNER JOIN patient_age a ON w.patient_id = a.patient_id
ORDER BY w.patient_id
;
