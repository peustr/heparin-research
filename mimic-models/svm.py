import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, mean_absolute_error, make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC, SVR

import scaler as sc

np.random.seed(10)

MIMIC_DATA_PATH = "../mimic-data/mimic_data.csv"


def get_svm_model(task_type, svm_hparams=None, hparam_tuning=True):
    """ task_type: 'classification' or 'regression' """
    df = pd.read_csv(MIMIC_DATA_PATH)
    df_train = df.query("set == 'train'")
    df_test = df.query("set == 'test'")
    X_train, y_train, X_test, y_test = sc.get_scaled_values(df_train, df_test)
    if svm_hparams is None or hparam_tuning:
        print("Tuning parameters...")
        svm_hparams, _ = tune_svm_model(X_train, y_train, task_type)
    if task_type == "classification":
        model = SVC(random_state=10, **svm_hparams)
    elif task_type == "regression":
        model = SVR(**svm_hparams)
    model.fit(X_train, y_train)
    return model


def tune_svm_model(X_train, y_train, task_type):
    param_grid = {
        "C": [
            np.power(2., -6), np.power(2., -5), np.power(2., -4),
            np.power(2., -3), np.power(2., -2), np.power(2., -1),
            1,
            np.power(2., 1), np.power(2., 2), np.power(2., 3),
            np.power(2., 4), np.power(2., 5), np.power(2., 6)
        ],
        "gamma": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    }
    if task_type == "classification":
        model = SVC(random_state=10)
        gs = GridSearchCV(
            model, param_grid,
            scoring=make_scorer(f1_score, average="micro"),
            cv=5)
    elif task_type == "regression":
        model = SVR()
        gs = GridSearchCV(
            model, param_grid,
            scoring=make_scorer(mean_absolute_error, greater_is_better=False),
            cv=5)
    gs.fit(X_train, y_train)
    return gs.best_params_, gs.best_score_
