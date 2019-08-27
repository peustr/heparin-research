import pandas as pd

df_mimic = pd.read_csv("mimic_lab_measurements.csv")

str_cohort_mimic = "(" + ", ".join(df_mimic.patient_id.apply(str).unique().tolist()) + ")"
with open("mimic-sql/cohort.txt", "w") as fp:
    fp.write(str_cohort_mimic)

with open("mimic-sql/patient_features_template.sql", "r") as fp:
    sql_cohort_mimic = fp.read()

sql_cohort_mimic = sql_cohort_mimic.replace("%REPLACE%", str_cohort_mimic)
with open("mimic-sql/patient_features.sql", "w") as fp:
    fp.write(sql_cohort_mimic)
