from fastapi import APIRouter, HTTPException
from typing import List, Dict
import random
from app.schemas.risk import RiskPredictionRequest, RiskPredictionResponse
from app.ml.predictor import predict_fire_risk
from app.services.risk_zone_service import RiskZoneService
from app.services.incident_service import incident_service

router = APIRouter()
risk_zone_service = RiskZoneService()

# Mock data generation for GET /api/risk
def generate_mock_risk_data() -> List[Dict]:
    regions = ["Northern California", "Southern California", "Oregon", "Washington", "Idaho", "Montana"]
    risk_data = []
    for region in regions:
        # Generate random risk score between 0 and 100
        risk_score = random.randint(0, 100)
        if risk_score <= 30:
            risk_level = "LOW"
        elif risk_score <= 60:
            risk_level = "MEDIUM"
        elif risk_score <= 80:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        risk_data.append({
            "region": region,
            "latitude": round(random.uniform(32.0, 49.0), 4),
            "longitude": round(random.uniform(-125.0, -110.0), 4),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "temperature": round(random.uniform(50.0, 100.0), 1),
            "humidity": round(random.uniform(10.0, 90.0), 1),
            "wind_speed": round(random.uniform(0.0, 30.0), 1),
            "rainfall": round(random.uniform(0.0, 10.0), 2)
        })
    return risk_data

@router.get("")
async def get_risk_data() -> List[Dict]:
    return generate_mock_risk_data()

@router.post("/predict", response_model=RiskPredictionResponse)
async def predict_risk(request: RiskPredictionRequest):
    """
    Predict fire risk based on environmental features.
    """
    try:
        # Convert Pydantic model to dict
        features = request.dict()
        # Get prediction
        result = predict_fire_risk(features)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/zones")
async def get_risk_zones() -> List[Dict]:
    """
    Get a grid of risk zones for visualization.
    Also processes each risk zone to create incidents and alerts.
    """
    try:
        risk_zones = risk_zone_service.get_risk_zones()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Process each risk zone to create incidents and alerts
    for zone in risk_zones:
        incident_service.process_risk_zone(zone, zone["latitude"], zone["longitude"])

    return risk_zones
