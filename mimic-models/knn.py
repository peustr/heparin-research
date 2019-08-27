import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier

import scaler as sc

np.random.seed(10)

MIMIC_DATA_PATH = "../mimic-data/mimic_data.csv"


def get_knn_model(knn_hparams=None, hparam_tuning=True):
    df = pd.read_csv(MIMIC_DATA_PATH)
    df_train = df.query("set == 'train'")
    df_test = df.query("set == 'test'")
    X_train, y_train, X_test, y_test = sc.get_scaled_values(df_train, df_test)
    if knn_hparams is None or hparam_tuning:
        print("Tuning parameters...")
        knn_hparams, best_score = tune_knn_model(X_train, y_train)
    model = KNeighborsClassifier(**knn_hparams)
    model.fit(X_train, y_train)
    return model


def tune_knn_model(X_train, y_train):
    param_grid = {
        "n_neighbors": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "weights": ["uniform", "distance"],
        "p": [1, 2, 3, 4, 5, 6]
    }
    model = KNeighborsClassifier()
    gs = GridSearchCV(
        model, param_grid,
        scoring=make_scorer(f1_score, average="micro"), cv=5)
    gs.fit(X_train, y_train)
    return gs.best_params_, gs.best_score_
