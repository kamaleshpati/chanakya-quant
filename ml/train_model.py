import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump
from features.feature_engg import create_features_labels

def train():
    df = pd.read_csv('data/market/raw/NIFTY50_minute_data.csv')  # Assume historical 1min or 5min
    X, y = create_features_labels(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    model_path = 'data/ml_model/pred_model.joblib'
    dump(clf, model_path)
    print(f"[ML] Model trained and saved to '{model_path}'")
