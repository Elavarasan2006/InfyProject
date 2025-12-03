import joblib

artifact = joblib.load("ml_models/jobrole_model.pkl")

if isinstance(artifact, dict):
    print("Model Keys:", artifact.keys())
    print("Feature Columns:", artifact.get("feature_columns"))
else:
    print("The model is not a dict. It contains:", type(artifact))
