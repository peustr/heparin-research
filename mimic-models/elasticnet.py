import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, make_scorer
from sklearn.model_selection import GridSearchCV

import scaler as sc

np.random.seed(10)

MIMIC_DATA_PATH = "../mimic-data/mimic_data.csv"


def get_knn_model(elasticnet_hparams=None, hparam_tuning=True):
    df = pd.read_csv(MIMIC_DATA_PATH)
    df_train = df.query("set == 'train'")
    df_test = df.query("set == 'test'")
    X_train, y_train, X_test, y_test = sc.get_scaled_values(df_train, df_test)
    if elasticnet_hparams is None or hparam_tuning:
        print("Tuning parameters...")
        elasticnet_hparams, best_score = tune_knn_model(X_train, y_train)
    model = ElasticNet(**elasticnet_hparams)
    model.fit(X_train, y_train)
    return model


def tune_knn_model(X_train, y_train):
    param_grid = {
        "alpha": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        "l1_ratio": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    }
    model = ElasticNet()
    gs = GridSearchCV(
        model, param_grid,
        scoring=make_scorer(mean_absolute_error, greater_is_better=False),
        cv=5)
    gs.fit(X_train, y_train)
    return gs.best_params_, gs.best_score_
