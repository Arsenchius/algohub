import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, log_loss
from optuna.trial import Trial
import numpy as np
import optuna

from preprocessing import resample_data, create_target


def objective(
    trial: Trial, df: pd.DataFrame, features: list[str], number_of_splits: int = 5
):
    tss = TimeSeriesSplit(n_splits=number_of_splits)
    df = df.sort_index()

    params = {
        # 'device': "gpu",
        "objective": "multiclass",
        "metric": "multi_logloss",
        "num_class": 3,
        "boosting_type": "gbdt",
        "lambda_l1": trial.suggest_loguniform("lambda_l1", 1e-8, 10.0),
        "lambda_l2": trial.suggest_loguniform("lambda_l2", 1e-8, 10.0),
        "num_leaves": trial.suggest_int("num_leaves", 2, 256),
        "feature_fraction": trial.suggest_uniform("feature_fraction", 0.4, 1.0),
        "verbose": -1,
    }

    scores = []

    for train_idx, test_idx in tss.split(df):
        train = df.iloc[train_idx]
        test = df.iloc[test_idx]

        X_train = train[features]
        y_train = train["Target"]

        X_test = test[features]
        y_test = test["Target"]

        model = lgb.train(
            params,
            lgb.Dataset(X_train, label=y_train),
            valid_sets=lgb.Dataset(X_test, label=y_test),
        )

        y_pred = model.predict(X_test)
        scores.append(log_loss(y_test, y_pred))

    return np.mean(scores)


def run():
    data = pd.read_csv("/home/kenny/algohub/data/data_eth_2018_2024.csv")
    data["Time"] = pd.to_datetime(data["Time"])
    data = data.set_index("Time")
    time_frames = [15, 30, 60, 240, 1440]
    new_data = resample_data(data, time_frames)
    new_data.dropna(inplace=True)
    new_data = create_target(new_data, future_time=10, size=1500)
    new_data["Target"] += 1
    new_data["Target"].value_counts()
    begin_date = pd.to_datetime("2018-01-01T00:00:00")
    end_date = pd.to_datetime("2023-01-01T00:00:00")

    new_data_train = new_data[(new_data.index <= end_date)].copy()
    new_data_test = new_data[(new_data.index > end_date)].copy()
    features = list(set(new_data.columns) - set(["Target"]))
    study = optuna.create_study(direction="minimize")
    func = lambda trial: objective(trial, new_data_train, features)
    study.optimize(func, n_trials=100)

    best_params = study.best_params
    best_params["objective"] = "multiclass"
    best_params["metric"] = "multi_logloss"
    best_params["num_class"] = 3
    best_params["boosting_type"] = "gbdt"
    best_params["verbose"] = -1

    X_train = new_data_train[features]
    y_train = new_data_train["Target"]

    X_test = new_data_test[features]
    y_test = new_data_test["Target"]

    model = lgb.train(
        best_params,
        lgb.Dataset(X_train, label=y_train),
        valid_sets=lgb.Dataset(X_test, label=y_test),
    )

    y_pred = model.predict(X_test)
    model.save_model("lgb_model.txt")


if __name__ == "__main__":
    run()
