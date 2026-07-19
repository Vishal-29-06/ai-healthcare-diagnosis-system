"""
Loads the trained model ONCE when the app starts (not on every
request — that would be slow and wasteful), and exposes a function
that turns raw patient data into a prediction + explanation.
"""

import joblib
import pandas as pd
import shap

_MODEL_DIR = "app/ml_models"

# These load once, when this module is first imported (i.e. once
# per server start), and stay in memory for every request after that.
model = joblib.load(f"{_MODEL_DIR}/heart_disease_model.pkl")
scaler = joblib.load(f"{_MODEL_DIR}/scaler.pkl")
feature_columns = joblib.load(f"{_MODEL_DIR}/feature_columns.pkl")

# The SHAP explainer is also expensive to build, so we build it once
# here rather than per-request.
explainer = shap.TreeExplainer(model)


def _build_feature_row(raw: dict) -> pd.DataFrame:
    """
    Takes the 13 raw clinical values and reproduces EXACTLY the same
    feature engineering we did during training (age bucketing +
    one-hot encoding) — otherwise the model would be fed data shaped
    differently than what it learned on, and predictions would be
    meaningless or error out entirely.
    """
    row = dict(raw)  # copy so we don't mutate the caller's dict

    age = row["age"]
    # Must match the same bins used in ml/prepare_features.py:
    # (0-40] = young, (40-55] = middle_aged, (55-100] = senior
    row["age_group_middle_aged"] = 1 if 40 < age <= 55 else 0
    row["age_group_senior"] = 1 if age > 55 else 0

    # Build a single-row DataFrame, then reindex to guarantee the
    # EXACT same column order the model was trained on. Mismatched
    # column order would silently produce wrong predictions, since
    # the model has no idea which number means what — it just sees
    # positions.
    df = pd.DataFrame([row])
    df = df.reindex(columns=feature_columns)
    return df


def predict_risk(raw_features: dict) -> dict:
    """
    The main function the API calls. Takes raw clinical values,
    returns a risk label, probability, and the top factors driving
    THIS specific prediction.
    """
    feature_row = _build_feature_row(raw_features)

    # Scale using the SAME scaler fitted during training — reusing
    # the training data's mean/std, never recalculating on new data.
    scaled_row = scaler.transform(feature_row)
    scaled_df = pd.DataFrame(scaled_row, columns=feature_columns)

    probability = model.predict_proba(scaled_df)[0][1]
    risk_label = "High risk" if probability >= 0.5 else "Low risk"

    # Explain THIS prediction specifically.
    shap_values = explainer.shap_values(scaled_df)
    if isinstance(shap_values, list):
        shap_for_disease = shap_values[1][0]
    elif shap_values.ndim == 3:
        shap_for_disease = shap_values[0, :, 1]
    else:
        shap_for_disease = shap_values[0]

    impact_series = pd.Series(shap_for_disease, index=feature_columns)
    top_5 = impact_series.reindex(impact_series.abs().sort_values(ascending=False).index).head(5)

    top_factors = [
        {
            "feature": feature,
            "impact": round(float(value), 4),
            "direction": "increased" if value > 0 else "decreased",
        }
        for feature, value in top_5.items()
    ]

    return {
        "risk_label": risk_label,
        "risk_probability": round(float(probability), 4),
        "top_factors": top_factors,
    }
