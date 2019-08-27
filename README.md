# heparin-research


## Install the dependencies

Navigate to the root of the project and run:

```bash
pip install -r requirements.txt
```

## Generate the MIMIC dataset

This tutorial assumes you have a PosgreSQL instance with the MIMIC database running.

First run the query in `mimic-data/mimic-sql/lab_measurements.sql`. This will give you a result set. Export it to CSV and name it `mimic_lab_measurements.csv`.

Then run the script in `mimic-data/build_query_for_features.py` like:
```bash
python build_query_for_features.py
```

This will generate a SQL file: `mimic-data/mimic-sql/patient_features.sql`. Run this SQL file in your local PostgreSQL instance. Export its results to `mimic_patient_featrures.csv`.

Then run the script in `mimic-data/join_measurements_and_features.py` like:
```bash
python join_measurements_and_features.py
```

This will generate a CSV file: `mimic_data.csv`. This is the MIMIC dataset used for training.
