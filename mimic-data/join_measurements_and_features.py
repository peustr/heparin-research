import pandas as pd

df_mimic_lab = pd.read_csv("mimic_lab_measurements.csv")
df_mimic_pat = pd.read_csv("mimic_patient_featrures.csv")

df_mimic_merged = df_mimic_lab.merge(
    df_mimic_pat, on="patient_id", how="inner")

df_mimic_merged.to_csv("mimic_data.csv", index=False)
