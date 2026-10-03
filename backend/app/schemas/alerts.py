from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    title: str
    message: str
    severity: str
    region: str
    risk_score: int
    source: str  # NASA FIRMS or FireSight Prediction

class AlertCreate(AlertBase):
    incident_id: str
    alert_type: str  # HOTSPOT_DETECTED, HIGH_FIRE_RISK, CRITICAL_FIRE_RISK

class Alert(AlertBase):
    id: str
    incident_id: str
    alert_type: str
    created_at: datetime
    status: str  # NEW, ACKNOWLEDGED, RESOLVED

    class Config:
        from_attributes = True
