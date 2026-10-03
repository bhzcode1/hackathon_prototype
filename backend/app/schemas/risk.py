"""
Pydantic schemas for fire risk prediction.
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any

class RiskPredictionRequest(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius", ge=10, le=50)
    humidity: float = Field(..., description="Relative humidity percentage", ge=0, le=100)
    wind_speed: float = Field(..., description="Wind speed in km/h", ge=0, le=60)
    rainfall: float = Field(..., description="Rainfall in mm", ge=0, le=100)
    vegetation_index: float = Field(..., description="Vegetation index (0-1)", ge=0, le=1)
    fuel_moisture: float = Field(..., description="Fuel moisture content (0-1)", ge=0, le=1)
    elevation: float = Field(..., description="Elevation in meters", ge=0, le=4000)
    slope: float = Field(..., description="Slope in degrees", ge=0, le=60)

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 38,
                "humidity": 25,
                "wind_speed": 32,
                "rainfall": 2,
                "vegetation_index": 0.65,
                "fuel_moisture": 0.18,
                "elevation": 850,
                "slope": 18
            }
        }

class RiskPredictionResponse(BaseModel):
    fire_probability: float = Field(..., description="Probability of fire occurrence (0-1)")
    risk_score: int = Field(..., description="Risk score scaled to 0-100")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, or CRITICAL")
    features: Dict[str, Any] = Field(..., description="Echo of input features")

    class Config:
        json_schema_extra = {
            "example": {
                "fire_probability": 0.87,
                "risk_score": 87,
                "risk_level": "CRITICAL",
                "features": {
                    "temperature": 38,
                    "humidity": 25,
                    "wind_speed": 32,
                    "rainfall": 2,
                    "vegetation_index": 0.65,
                    "fuel_moisture": 0.18,
                    "elevation": 850,
                    "slope": 18
                }
            }
        }