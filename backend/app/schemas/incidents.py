from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IncidentBase(BaseModel):
    title: str
    region: str
    latitude: float
    longitude: float
    risk_score: int
    risk_level: str
    hotspot_id: Optional[str] = None
    hotspot_confidence: Optional[float] = None
    frp: Optional[float] = None
    severity: str
    source: str

class IncidentCreate(IncidentBase):
    pass

class Incident(IncidentBase):
    id: str
    status: str  # DETECTED, ACTIVE, ACKNOWLEDGED, RESOLVED
    detected_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
