from fastapi import APIRouter, HTTPException
from typing import List, Any, Dict
from datetime import datetime
import json
import traceback
from pathlib import Path
from app.services.store import store
from app.services.ai_incident_service import AIIncidentService
from app.schemas.alerts import Alert

router = APIRouter()

# #region agent log
_DEBUG_LOG = Path(__file__).resolve().parents[4] / ".cursor" / "debug-27ea16.log"

def _agent_log(hypothesis_id: str, location: str, message: str, data: dict, run_id: str = "post-fix"):
    try:
        _DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "sessionId": "27ea16",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
        }
        with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=str) + "\n")
    except Exception:
        pass
# #endregion

# Initialize AI service for alert analysis
ai_service = AIIncidentService()


def _normalize_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coerce in-memory alert dicts into the Alert schema shape.
    Legacy records may use `type` instead of `alert_type`, or store a float risk_score.
    """
    normalized = dict(alert)
    if "alert_type" not in normalized and "type" in normalized:
        normalized["alert_type"] = normalized.pop("type")
    if "message" not in normalized or normalized["message"] is None:
        normalized["message"] = normalized.get("title") or "Alert"
    risk = normalized.get("risk_score", 0)
    try:
        normalized["risk_score"] = int(round(float(risk)))
    except (TypeError, ValueError):
        normalized["risk_score"] = 0
    created = normalized.get("created_at")
    if isinstance(created, datetime):
        normalized["created_at"] = created.isoformat()
    for key in ("title", "severity", "region", "source", "status", "incident_id", "alert_type"):
        if key not in normalized or normalized[key] is None:
            normalized[key] = "" if key != "status" else "NEW"
    return normalized


@router.get("", response_model=List[Alert])
async def get_alerts():
    """
    Get all alerts.
    """
    # #region agent log
    _agent_log("A", "alerts.py:get_alerts:entry", "get_alerts entered", {"alerts_in_store": len(store.alerts)})
    # #endregion
    try:
        raw = store.get_alerts()
        alerts = [_normalize_alert(a) for a in raw]
        # #region agent log
        sample = alerts[0] if alerts else None
        validation_errors = []
        for i, alert in enumerate(alerts[:5]):
            try:
                Alert.model_validate(alert)
            except Exception as ve:
                validation_errors.append({"index": i, "error": str(ve)})
        _agent_log(
            "A,B,C",
            "alerts.py:get_alerts:pre-return",
            "about to return normalized alerts",
            {
                "count": len(alerts),
                "sample_keys": list(sample.keys()) if sample else None,
                "sample_types": {k: type(v).__name__ for k, v in sample.items()} if sample else None,
                "validation_errors": validation_errors,
            },
        )
        # #endregion
        return alerts
    except Exception as e:
        # #region agent log
        _agent_log(
            "A",
            "alerts.py:get_alerts:exception",
            "exception in get_alerts body",
            {"error": str(e), "traceback": traceback.format_exc()},
            run_id="pre-fix",
        )
        # #endregion
        raise


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """
    Get a single alert by ID.
    """
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _normalize_alert(alert)


@router.post("/{alert_id}/acknowledge", response_model=Alert)
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge an alert.
    """
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert["status"] != "NEW":
        raise HTTPException(status_code=400, detail="Alert cannot be acknowledged in current status")
    updated = store.update_alert(alert_id, {"status": "ACKNOWLEDGED"})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update alert")
    return _normalize_alert(updated)


@router.post("/{alert_id}/resolve", response_model=Alert)
async def resolve_alert(alert_id: str):
    """
    Resolve an alert.
    """
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert["status"] != "ACKNOWLEDGED":
        raise HTTPException(status_code=400, detail="Alert cannot be resolved in current status")
    updated = store.update_alert(alert_id, {"status": "RESOLVED"})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update alert")
    return _normalize_alert(updated)


@router.post("/{alert_id}/analyze")
async def analyze_alert(alert_id: str):
    """
    Generate AI analysis for an alert.
    If analysis already exists, return it unless regeneration is requested via a different endpoint.
    """
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Check if we already have an analysis
    existing_analysis = store.get_alert_analysis(alert_id)
    if existing_analysis is not None:
        return {
            "alert_id": alert_id,
            "provider": existing_analysis.get("provider", "unknown"),
            "analysis": existing_analysis
        }

    # Gather data for analysis (we'll pass None for optional data for now)
    risk_data = None
    hotspot_data = None
    environmental_data = None

    analysis_obj = ai_service.analyze_incident(
        incident=alert,  # Alert has similar structure to incident for analysis purposes
        risk_data=risk_data,
        hotspot_data=hotspot_data,
        environmental_data=environmental_data
    )

    # Store the analysis
    store.set_alert_analysis(alert_id, analysis_obj.to_dict())

    return {
        "alert_id": alert_id,
        "provider": analysis_obj.provider,
        "analysis": analysis_obj.to_dict()
    }


@router.post("/{alert_id}/analyze/regenerate")
async def regenerate_alert_analysis(alert_id: str):
    """
    Regenerate AI analysis for an alert, ignoring any cached analysis.
    """
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Gather data for analysis (same as above)
    risk_data = None
    hotspot_data = None
    environmental_data = None

    analysis_obj = ai_service.analyze_incident(
        incident=alert,  # Alert has similar structure to incident for analysis purposes
        risk_data=risk_data,
        hotspot_data=hotspot_data,
        environmental_data=environmental_data
    )

    # Store the new analysis (overwriting the old one)
    store.set_alert_analysis(alert_id, analysis_obj.to_dict())

    return {
        "alert_id": alert_id,
        "provider": analysis_obj.provider,
        "analysis": analysis_obj.to_dict()
    }
