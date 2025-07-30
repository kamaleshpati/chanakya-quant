import pandas as pd
from joblib import load, dump
from sklearn.ensemble import RandomForestClassifier
from features.feature_engg import create_features_labels

model_path = 'ml_model/model/rf_model.joblib'

def update_model(new_data_path='ml_model/features/signals_log.csv'):
    model = load(model_path)
    df = pd.read_csv(new_data_path)
    X, y = create_features_labels(df)

    if hasattr(model, 'partial_fit'):
        model.partial_fit(X, y)
    else:
        print("[ML] Model does not support online learning.")

    dump(model, model_path)
    print("[ML] Model updated with new signals.")

if __name__ == "__main__":
    update_model()
