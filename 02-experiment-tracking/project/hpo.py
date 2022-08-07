import argparse
import os
import pickle

import numpy as np
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from hyperopt.pyll import scope
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


import mlflow

os.environ['AWS_PROFILE'] = "default"

TRACKING_SERVER_HOST = "ec2-18-224-56-159.us-east-2.compute.amazonaws.com"
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
mlflow.set_experiment("random-forest-experiment")

def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def run(data_path:str, num_trials:int):

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_valid, y_valid = load_pickle(os.path.join(data_path, "valid.pkl"))

    def objective(params):
        with mlflow.start_run():
            mlflow.log_params(params)
            rf = RandomForestRegressor(**params)
            rf.fit(X_train, y_train)
            
            y_pred = rf.predict(X_valid)
            rmse = mean_squared_error(y_valid, y_pred, squared = False)
            mlflow.log_metric("rmse", rmse)

        return {'loss' : rmse, 'status': STATUS_OK}

    search_space = {
        'max_depth': scope.int(hp.quniform('max_depth', 1, 20, 1)),
        'n_estimators': scope.int(hp.quniform('n_estimators', 10, 50, 1)),
        'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 10, 1)),
        'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 4, 1)),
        'random_state': 42
    }
    rstate = np.random.default_rng(42)  # for reproducible results

    fmin(
        fn=objective, # Return rmse -> finding minimum rmse
        space=search_space,
        algo=tpe.suggest,
        max_evals=num_trials,
        trials=Trials(),
        rstate=rstate
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        default="./output",
        help = "Location where processed NYC taxi trip data was saved"
    )
    parser.add_argument(
        "--max_evals",
        type = int,
        default = 50,
        help = "Number of parameters evaluation for the optimizer to explore"
    )
    args = parser.parse_args()

    run(args.data_path, args.max_evals)



