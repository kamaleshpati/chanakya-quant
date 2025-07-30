import pandas as pd
from joblib import load
from features.feature_engineering import create_features_only

model_path = 'data/ml_model/rf_model.joblib'
clf = load(model_path)

def predict(df: pd.DataFrame):
    X = create_features_only(df)
    pred = clf.predict(X)
    conf = clf.predict_proba(X).max(axis=1)
    return pred, conf
