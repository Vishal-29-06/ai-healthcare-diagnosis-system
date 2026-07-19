"""
Step 3: Train and compare two models, pick the better one.

Run with: python ml/train_model.py
"""

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# Load everything we prepared in Step 2.
X_train = joblib.load("ml/saved_models/X_train_scaled.pkl")
X_test = joblib.load("ml/saved_models/X_test_scaled.pkl")
y_train = joblib.load("ml/saved_models/y_train.pkl")
y_test = joblib.load("ml/saved_models/y_test.pkl")


def evaluate(name, model, X_test, y_test):
    """
    Runs the model on the held-out test set (data it never saw during
    training) and prints out how well it actually generalizes.
    """
    predictions = model.predict(X_test)

    print(f"\n{'=' * 50}")
    print(f"{name}")
    print("=" * 50)
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.3f}")
    print(f"Precision: {precision_score(y_test, predictions):.3f}")
    print(f"Recall:    {recall_score(y_test, predictions):.3f}")
    print(f"F1-score:  {f1_score(y_test, predictions):.3f}")

    # A confusion matrix breaks predictions into 4 buckets:
    # [[true_negatives,  false_positives],
    #  [false_negatives, true_positives]]
    # false_negatives is the one to watch most closely here — those
    # are sick patients the model incorrectly said were healthy.
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    return recall_score(y_test, predictions)


# --- Model 1: Logistic Regression ---
log_reg = LogisticRegression(random_state=42, max_iter=1000)
log_reg.fit(X_train, y_train)
log_reg_recall = evaluate("Logistic Regression", log_reg, X_test, y_test)

# --- Model 2: Random Forest ---
rand_forest = RandomForestClassifier(n_estimators=100, random_state=42)
rand_forest.fit(X_train, y_train)
rf_recall = evaluate("Random Forest", rand_forest, X_test, y_test)

# --- Pick the winner based on recall (catching real disease cases) ---
if rf_recall >= log_reg_recall:
    best_model = rand_forest
    best_name = "Random Forest"
else:
    best_model = log_reg
    best_name = "Logistic Regression"

print(f"\n{'=' * 50}")
print(f"WINNER: {best_name} (higher recall = fewer missed diagnoses)")
print("=" * 50)

# Save the winning model — this .pkl file is what our FastAPI app
# will load in the next phase to actually make live predictions.
joblib.dump(best_model, "ml/saved_models/heart_disease_model.pkl")
joblib.dump(best_name, "ml/saved_models/model_name.pkl")
print(f"\nSaved winning model to ml/saved_models/heart_disease_model.pkl")
