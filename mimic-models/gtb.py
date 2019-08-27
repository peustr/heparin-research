import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import f1_score, mean_absolute_error, make_scorer
from sklearn.model_selection import GridSearchCV

import scaler as sc

np.random.seed(10)

MIMIC_DATA_PATH = "../mimic-data/mimic_data.csv"


def get_xgb_model(task_type, xgb_hparams=None, hparam_tuning=True):
    """ task_type: 'classification' or 'regression' """
    df = pd.read_csv(MIMIC_DATA_PATH)
    df_train = df.query("set == 'train'")
    df_test = df.query("set == 'test'")
    X_train, y_train, X_test, y_test = sc.get_scaled_values(df_train, df_test)
    if xgb_hparams is None or hparam_tuning:
        print("Tuning parameters...")
        xgb_hparams, _ = tune_xgb_model(X_train, y_train, task_type)
    if task_type == "classification":
        model = xgb.XGBClassifier(
            random_state=10, **xgb_hparams)
    elif task_type == "regression":
        model = xgb.XGBRegressor(
            random_state=10, objective="reg:squarederror", **xgb_hparams)
    model.fit(X_train, y_train)
    return model


def tune_xgb_model(X_train, y_train, task_type):
    param_grid = {
        "n_estimators": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        "learning_rate": [0.1, 0.05, 0.01],
        "max_depth": [2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    if task_type == "classification":
        model = xgb.XGBClassifier(random_state=10)
        gs = GridSearchCV(
            model, param_grid,
            scoring=make_scorer(f1_score, average="micro"),
            cv=5)
    elif task_type == "regression":
        model = xgb.XGBRegressor(random_state=10)
        gs = GridSearchCV(
            model, param_grid,
            scoring=make_scorer(mean_absolute_error, greater_is_better=False),
            cv=5)
    gs.fit(X_train, y_train)
    return gs.best_params_, gs.best_score_
