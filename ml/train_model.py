import pandas as pd
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import joblib

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
df = pd.read_excel("ml/jobrole_dataset.xlsx", engine="openpyxl")
df.columns = df.columns.str.strip()

# -------------------------------------------------------
# HANDLE MULTI-VALUE COLUMNS
# -------------------------------------------------------
def split_multi_value(col):
    return (
        col.fillna("")  
           .astype(str)
           .apply(lambda x: [i.strip() for i in x.split(",") if i.strip()])
    )

df["Skills"] = split_multi_value(df["Skills"])
df["Certification"] = split_multi_value(df["Certification"])

# Convert multi-value → one-hot
mlb_skills = MultiLabelBinarizer()
skills_encoded = mlb_skills.fit_transform(df["Skills"])
skills_df = pd.DataFrame(skills_encoded, columns=[f"skill_{s}" for s in mlb_skills.classes_])

mlb_cert = MultiLabelBinarizer()
cert_encoded = mlb_cert.fit_transform(df["Certification"])
cert_df = pd.DataFrame(cert_encoded, columns=[f"cert_{c}" for c in mlb_cert.classes_])

df = pd.concat([df, skills_df, cert_df], axis=1)

# -------------------------------------------------------
# ENCODE SINGLE TEXT COLUMNS
# -------------------------------------------------------
label_cols = ["Degree", "Major", "Specialization", "Preferred Industry"]
encoders = {}

for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

# -------------------------------------------------------
# ENCODE TARGET (Job Role)
# -------------------------------------------------------
target_encoder = LabelEncoder()
df["JobRoleEncoded"] = target_encoder.fit_transform(df["Job Role"])

# -------------------------------------------------------
# TRAINING DATA
# -------------------------------------------------------
X = df.drop(columns=["Skills", "Certification", "Job Role", "JobRoleEncoded"])
y = df["JobRoleEncoded"]

# -------------------------------------------------------
# TRAIN-TEST SPLIT
# -------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------------
# XGBOOST MODEL
# -------------------------------------------------------
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.9,
    eval_metric="mlogloss"
)

model.fit(X_train, y_train)

# -------------------------------------------------------
# EVALUATION
# -------------------------------------------------------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("\nModel Accuracy:", acc)

# -------------------------------------------------------
# SAVE ALL ARTIFACTS
# -------------------------------------------------------
joblib.dump(model, "ml/jobrole_model.pkl")
joblib.dump(target_encoder, "ml/jobrole_target_encoder.pkl")
joblib.dump(encoders, "ml/text_label_encoders.pkl")
joblib.dump(mlb_skills, "ml/multilabel_skills.pkl")
joblib.dump(mlb_cert, "ml/multilabel_cert.pkl")
print("Total rows loaded:", len(df))

print("Model Accuracy (%):", accuracy_score(y_test, y_pred) * 100)






print("\nModel and encoders saved successfully!")


