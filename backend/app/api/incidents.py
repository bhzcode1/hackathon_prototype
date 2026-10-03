from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from datetime import datetime
from app.services.store import store
from app.services.ai_incident_service import AIIncidentService
from app.services.incident_service import incident_service
from app.services.firms_service import FirmsService
from app.schemas.incidents import Incident
from app.schemas.alerts import Alert

router = APIRouter()
ai_service = AIIncidentService()
firms_service = FirmsService()

@router.get("", response_model=List[Incident])
async def get_incidents():
    """
    Get all incidents.
    """
    return store.get_incidents()

@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str):
    """
    Get a single incident by ID.
    """
    incident = store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{incident_id}/acknowledge", response_model=Incident)
async def acknowledge_incident(incident_id: str):
    """
    Acknowledge an incident.
    """
    incident = store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident["status"] not in ["DETECTED", "ACTIVE"]:
        raise HTTPException(status_code=400, detail="Incident cannot be acknowledged in current status")
    update_data = {
        "status": "ACKNOWLEDGED",
        "acknowledged_at": datetime.utcnow()
    }
    updated = store.update_incident(incident_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update incident")
    return updated

@router.post("/{incident_id}/resolve", response_model=Incident)
async def resolve_incident(incident_id: str):
    """
    Resolve an incident.
    """
    incident = store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident["status"] not in ["ACKNOWLEDGED", "ACTIVE"]:
        raise HTTPException(status_code=400, detail="Incident cannot be resolved in current status")
    update_data = {
        "status": "RESOLVED",
        "resolved_at": datetime.utcnow()
    }
    updated = store.update_incident(incident_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update incident")
    return updated

@router.post("/{incident_id}/analyze")
async def analyze_incident(incident_id: str):
    """
    Generate AI analysis for an incident.
    If analysis already exists, return it unless regeneration is requested via a different endpoint.
    """
    incident = store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Check if we already have an analysis
    existing_analysis = store.get_incident_analysis(incident_id)
    if existing_analysis is not None:
        return {
            "incident_id": incident_id,
            "provider": existing_analysis.get("provider", "unknown"),
            "analysis": existing_analysis
        }

    # Gather data for analysis
    risk_data = None
    hotspot_data = None
    environmental_data = None

    # Prepare the data for the AI service
    # We'll pass the incident as is, and None for the optional data.
    analysis_obj = ai_service.analyze_incident(
        incident=incident,
        risk_data=risk_data,
        hotspot_data=hotspot_data,
        environmental_data=environmental_data
    )

    # Store the analysis
    store.set_incident_analysis(incident_id, analysis_obj.to_dict())

    return {
        "incident_id": incident_id,
        "provider": analysis_obj.provider,
        "analysis": analysis_obj.to_dict()
    }

@router.post("/{incident_id}/analyze/regenerate")
async def regenerate_incident_analysis(incident_id: str):
    """
    Regenerate AI analysis for an incident, ignoring any cached analysis.
    """
    incident = store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Gather data for analysis (same as above)
    risk_data = None
    hotspot_data = None
    environmental_data = None

    analysis_obj = ai_service.analyze_incident(
        incident=incident,
        risk_data=risk_data,
        hotspot_data=hotspot_data,
        environmental_data=environmental_data
    )

    # Store the new analysis (overwriting the old one)
    store.set_incident_analysis(incident_id, analysis_obj.to_dict())

    return {
        "incident_id": incident_id,
        "provider": analysis_obj.provider,
        "analysis": analysis_obj.to_dict()
    }