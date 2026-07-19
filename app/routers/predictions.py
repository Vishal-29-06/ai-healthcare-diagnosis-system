import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.prediction import PredictionInput, PredictionOutput
from app.core.dependencies import get_current_user, require_role
from app.core.ml_predictor import predict_risk
from app.models.user import UserRole
from app.routers.records import _get_record_or_403

router = APIRouter(prefix="/predictions", tags=["Disease Prediction"])


@router.post("/predict", response_model=PredictionOutput)
def predict(
    payload: PredictionInput,
    current_user: User = Depends(get_current_user),
):
    """
    Standalone prediction — any logged-in user (patient or doctor)
    can submit clinical values and get an immediate risk assessment.
    Doesn't save anything; useful as a quick 'what-if' calculator.
    """
    result = predict_risk(payload.model_dump())
    return result


@router.post("/records/{record_id}/predict-risk", response_model=PredictionOutput)
def predict_and_save_to_record(
    record_id: int,
    payload: PredictionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    """
    Doctor-only: runs a prediction AND saves the risk_score +
    explanation directly onto an existing medical record — this is
    what actually populates the risk_score/risk_explanation fields
    we left empty back in Phase 5.
    """
    record = _get_record_or_403(record_id, current_user, db)

    result = predict_risk(payload.model_dump())

    record.risk_score = result["risk_probability"]
    # Text column, so we store the explanation as readable text
    # rather than a nested object (keeps it human-readable if anyone
    # queries the database directly, e.g. in Workbench).
    record.risk_explanation = json.dumps(result["top_factors"])

    db.commit()
    db.refresh(record)

    return result
