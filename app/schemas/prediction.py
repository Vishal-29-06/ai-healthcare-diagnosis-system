from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """
    The 13 clinical measurements our model was trained on. Field()
    constraints reject obviously invalid values before we even run
    the model (e.g. a negative age).
    """
    age: int = Field(ge=1, le=120)
    sex: int = Field(ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(ge=0, le=3, description="Chest pain type (0-3)")
    trestbps: int = Field(ge=50, le=250, description="Resting blood pressure")
    chol: int = Field(ge=100, le=600, description="Cholesterol")
    fbs: int = Field(ge=0, le=1, description="Fasting blood sugar > 120 mg/dl")
    restecg: int = Field(ge=0, le=2, description="Resting ECG result")
    thalach: int = Field(ge=60, le=220, description="Max heart rate achieved")
    exang: int = Field(ge=0, le=1, description="Exercise-induced angina")
    oldpeak: float = Field(ge=0, le=10, description="ST depression")
    slope: int = Field(ge=0, le=2)
    ca: int = Field(ge=0, le=4, description="Number of major vessels")
    thal: int = Field(ge=0, le=3)


class RiskFactor(BaseModel):
    feature: str
    impact: float
    direction: str  # "increased" or "decreased"


class PredictionOutput(BaseModel):
    risk_label: str  # "High risk" or "Low risk"
    risk_probability: float  # 0.0 to 1.0
    top_factors: list[RiskFactor]
