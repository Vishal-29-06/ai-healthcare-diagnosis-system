"""
Step 2: Feature engineering + train/test split.

Run with: python ml/prepare_features.py
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv("ml/data/heart.csv")

# --- Feature engineering: derive an age_group column ---
# pd.cut() slices a numeric column into labeled buckets based on
# the ranges (bins) we specify. This gives the model an additional,
# differently-shaped signal beyond the raw age number.
df["age_group"] = pd.cut(
    df["age"],
    bins=[0, 40, 55, 100],
    labels=["young", "middle_aged", "senior"],
)

# Models can't use text labels directly — they need numbers. This
# converts age_group into separate 0/1 columns, one per category
# (a technique called "one-hot encoding"). drop_first=True avoids
# creating redundant columns (if it's not young and not middle_aged,
# we already know it must be senior, so we don't need a third column).
df = pd.get_dummies(df, columns=["age_group"], drop_first=True)

print("Columns after feature engineering:")
print(df.columns.tolist())

# --- Split into features (X) and target (y) ---
X = df.drop("target", axis=1)
y = df["target"]

# --- Train/test split ---
# stratify=y ensures BOTH the train and test sets keep roughly the
# same 165/138 balance we saw earlier, instead of risking an unlucky
# split where the test set ends up mostly one class by chance.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {X_train.shape[0]} patients")
print(f"Test set size: {X_test.shape[0]} patients")

# --- Scale numeric features ---
# fit_transform on the TRAINING data: this calculates the mean/std
# from training data only, then applies the scaling.
# transform (NOT fit_transform) on the TEST data: we reuse the SAME
# mean/std learned from training. This matters — if we let the test
# set influence the scaling, we'd be leaking information from data
# the model is supposed to have never seen, making our evaluation
# dishonestly optimistic.
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save everything we'll need in the next step (training), so we
# don't have to redo this work every time.
joblib.dump(X_train_scaled, "ml/saved_models/X_train_scaled.pkl")
joblib.dump(X_test_scaled, "ml/saved_models/X_test_scaled.pkl")
joblib.dump(y_train, "ml/saved_models/y_train.pkl")
joblib.dump(y_test, "ml/saved_models/y_test.pkl")
joblib.dump(scaler, "ml/saved_models/scaler.pkl")
joblib.dump(X.columns.tolist(), "ml/saved_models/feature_columns.pkl")

print("\nSaved prepared data + scaler to ml/saved_models/")
