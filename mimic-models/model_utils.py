import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from sklearn.metrics import (
    f1_score, confusion_matrix,
    mean_absolute_error, mean_squared_error)


def binary_classification_predict(model, X_test, y_test):
    y_pred = model.predict(X_test)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    print("\tPOS\tNEG\nT\t{}\t{}\nF\t{}\t{}".format(tp, tn, fp, fn))

    vf1_score = f1_score(y_test, y_pred, average="micro")
    print("F1-Score: {}".format(vf1_score))

    return tp, fp, tn, fn, vf1_score


def regression_predict(model, X_test, y_test):
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(mae)
    print(rmse)

    plot_actual_vs_predicted(y_test, y_pred)

    return mae, rmse


def plot_actual_vs_predicted(y_test, y_pred):
    matplotlib.rc('font', **{'size': 16})
    plt.figure(figsize=(10, 10))
    plt.xlim(np.min(y_test), 120)
    plt.ylim(np.min(y_test), 120)
    plt.xlabel("Predictions")
    plt.ylabel("True values")
    plt.scatter(
        y_pred, y_test,
        s=10, c="#1c2938", alpha=0.5,
        label="Predictions")
    plt.plot(
        y_test, y_test,
        color="#cd3f3e", linewidth=0.5, linestyle="--", dashes=(5, 20),
        label="Ideal Predictions")
    # Therapeutic range.
    plt.gca().add_patch(
        Rectangle((60, 60), 20, 20, color="#1c2938", alpha=0.1))
    plt.legend(loc="lower right")
    plt.show()
