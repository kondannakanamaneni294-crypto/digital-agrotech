from pydantic import BaseModel, Field
from typing import List, Optional

class EnvironmentData(BaseModel):
    latitude: float
    longitude: float
    temperature_celsius: float
    soil_moisture_0_to_1cm: float
    soil_moisture_1_to_3cm: Optional[float] = None
    units: Optional[dict] = None

class DiagnosisPrediction(BaseModel):
    label: str
    score: float

class DiagnosisResponse(BaseModel):
    status: str
    model_used: str
    predictions: List[DiagnosisPrediction]
    top_prediction: str
    confidence: float

class AdvisoryRequest(BaseModel):
    crop_type: str = Field(..., example="Tomato")
    crop_status: str = Field(..., example="Early blight identified with brown spot spots on leaves")
    latitude: Optional[float] = Field(None, example=37.7749)
    longitude: Optional[float] = Field(None, example=-122.4194)
    temperature_celsius: Optional[float] = Field(None, example=24.5)
    soil_moisture: Optional[float] = Field(None, example=0.25)

class AdvisoryStep(BaseModel):
    step_number: int
    title: str
    action: str
    rationale: str

class AdvisoryResponse(BaseModel):
    status: str
    crop_type: str
    crop_status: str
    environment_summary: dict
    advisory_summary: str
    three_step_advisory: List[AdvisoryStep]
