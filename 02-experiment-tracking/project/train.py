import argparse
import os
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

import mlflow

os.environ['AWS_PROFILE'] = "default"

TRACKING_SERVER_HOST = "ec2-18-224-56-159.us-east-2.compute.amazonaws.com"
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
mlflow.set_experiment("random-forest-experiment")
mlflow.sklearn.autolog()

def load_pickle(filename:str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)

def run(data_path:str):
    with mlflow.start_run():
        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_valid, y_valid = load_pickle(os.path.join(data_path, "valid.pkl"))

        rf = RandomForestRegressor(max_depth = 10 , random_state = 0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_valid)

        rmse = mean_squared_error(y_valid, y_pred, squared = False)
        mlflow.log_metric("rmse", rmse)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        default = "./output",
        help = "Localtion where processed NYC taxi trip data was saved"
    )
    args = parser.parse_args()

    run(args.data_path)