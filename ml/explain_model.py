"""
Step 4: Explainability with SHAP.

Run with: python ml/explain_model.py
"""

import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

# Load the trained model and data.
model = joblib.load("ml/saved_models/heart_disease_model.pkl")
X_test = joblib.load("ml/saved_models/X_test_scaled.pkl")
feature_columns = joblib.load("ml/saved_models/feature_columns.pkl")

# X_test is currently a plain numpy array (that's what StandardScaler
# outputs) — we wrap it back into a DataFrame with real column names
# so SHAP's charts show "chol", "age" etc. instead of "column 0, 1, 2".
X_test_df = pd.DataFrame(X_test, columns=feature_columns)

# TreeExplainer is a version of SHAP optimized specifically for
# tree-based models (Random Forest, XGBoost, etc.) — much faster
# than the generic explainer for this kind of model.
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test_df)

# Different versions of SHAP return this in different shapes:
# - a list of two arrays (one per class), or
# - a single 3D array shaped (patients, features, classes)
# This handles both, so the script doesn't break on a version bump.
if isinstance(shap_values, list):
    shap_values_for_disease = shap_values[1]
elif shap_values.ndim == 3:
    shap_values_for_disease = shap_values[:, :, 1]
else:
    shap_values_for_disease = shap_values

# --- Global explanation: which features matter most OVERALL ---
# This averages the impact of each feature across every patient in
# the test set — answers "what does this model generally pay
# attention to?"
mean_abs_shap = pd.Series(
    abs(shap_values_for_disease).mean(axis=0), index=feature_columns
).sort_values(ascending=False)

print("=" * 50)
print("GLOBAL FEATURE IMPORTANCE (average impact across all patients)")
print("=" * 50)
print(mean_abs_shap)

# Save a summary chart — useful to literally put in your README or
# resume portfolio as a screenshot showing explainability in action.
plt.figure()
shap.summary_plot(shap_values_for_disease, X_test_df, show=False)
plt.tight_layout()
plt.savefig("ml/saved_models/shap_summary.png", dpi=150)
print("\nSaved chart to ml/saved_models/shap_summary.png")

# --- Local explanation: explain ONE specific patient's prediction ---
# This is what our API will actually do live for each new patient —
# explain THIS prediction, not the model in general.
sample_index = 0
sample_patient = X_test_df.iloc[[sample_index]]
prediction = model.predict(sample_patient)[0]
prediction_proba = model.predict_proba(sample_patient)[0][1]

print("\n" + "=" * 50)
print(f"EXAMPLE: explaining one specific patient (test row {sample_index})")
print("=" * 50)
print(f"Predicted: {'Has heart disease' if prediction == 1 else 'No heart disease'}")
print(f"Risk probability: {prediction_proba:.2%}")

patient_shap_values = pd.Series(
    shap_values_for_disease[sample_index], index=feature_columns
).sort_values(key=abs, ascending=False)

print("\nTop factors driving THIS prediction:")
for feature, value in patient_shap_values.head(5).items():
    direction = "increased" if value > 0 else "decreased"
    print(f"  {feature}: {direction} risk (impact: {value:+.3f})")
