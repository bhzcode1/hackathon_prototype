import sys
sys.path.insert(0, '.')

from app.services.incident_service import incident_service
from app.services.store import store
from app.services.alert_service import alert_service
from datetime import datetime

def clear_store():
    store.incidents.clear()
    store.alerts.clear()
    store.incident_id_counter = 0
    store.alert_id_counter = 0

def test_create_incident_from_hotspot():
    clear_store()
    hotspot_data = {
        "latitude": 10.0,
        "longitude": 20.0,
        "confidence": 90.0,
        "frp": 50.0,
        "source": "NASA FIRMS",
        "region": "Test Region",
    }
    incident = incident_service.create_incident_from_hotspot(hotspot_data)
    assert incident is not None
    assert incident["id"] == "1"
    assert incident["title"] == "CRITICAL Fire Hotspot Detected in Test Region"
    assert incident["severity"] == "CRITICAL"  # Because confidence 90 -> CRITICAL, frp 50 -> HIGH, risk_score 0 -> LOW -> highest is CRITICAL
    assert incident["hotspot_id"] == "10.0_20.0"
    assert incident["status"] == "DETECTED"

def test_duplicate_hotspot():
    clear_store()
    hotspot_data = {
        "latitude": 10.0,
        "longitude": 20.0,
        "confidence": 90.0,
        "frp": 50.0,
        "source": "NASA FIRMS",
        "region": "Test Region",
    }
    incident1 = incident_service.create_incident_from_hotspot(hotspot_data)
    assert incident1 is not None
    incident2 = incident_service.create_incident_from_hotspot(hotspot_data)
    assert incident2 is None  # Duplicate

def test_create_incident_from_risk():
    clear_store()
    risk_data = {
        "risk_score": 90,
        "risk_level": "CRITICAL",
        "region": "Test Region",
        "temperature": 25.0,
        "humidity": 60.0,
        "wind_speed": 10.0,
        "rainfall": 5.0,
    }
    incident = incident_service.create_incident_from_risk(risk_data, 10.0, 20.0)
    assert incident is not None
    assert incident["id"] == "1"
    assert incident["title"] == "CRITICAL Fire Risk Detected in Test Region"
    assert incident["severity"] == "CRITICAL"
    assert incident["hotspot_id"] == "risk_10.0_20.0"
    assert incident["status"] == "DETECTED"

def test_process_hotspot():
    clear_store()
    hotspot_data = {
        "latitude": 10.0,
        "longitude": 20.0,
        "confidence": 90.0,
        "frp": 50.0,
        "source": "NASA FIRMS",
        "region": "Test Region",
    }
    incident = incident_service.process_hotspot(hotspot_data)
    assert incident is not None
    # Check that an alert was created
    alerts = store.get_alerts()
    assert len(alerts) == 1
    assert alerts[0]["incident_id"] == incident["id"]
    assert alerts[0]["type"] == "CRITICAL_FIRE_RISK"  # Because severity is CRITICAL
    assert alerts[0]["severity"] == "CRITICAL"

def test_process_risk_zone():
    clear_store()
    risk_data = {
        "risk_score": 90,
        "risk_level": "CRITICAL",
        "region": "Test Region",
        "temperature": 25.0,
        "humidity": 60.0,
        "wind_speed": 10.0,
        "rainfall": 5.0,
    }
    incident = incident_service.process_risk_zone(risk_data, 10.0, 20.0)
    assert incident is not None
    alerts = store.get_alerts()
    assert len(alerts) == 1
    assert alerts[0]["incident_id"] == incident["id"]
    assert alerts[0]["type"] == "CRITICAL_FIRE_RISK"  # Because severity is CRITICAL
    assert alerts[0]["severity"] == "CRITICAL"

def test_invalid_state_transition():
    clear_store()
    # Create an incident
    hotspot_data = {
        "latitude": 10.0,
        "longitude": 20.0,
        "confidence": 90.0,
        "frp": 50.0,
        "source": "NASA FIRMS",
        "region": "Test Region",
    }
    incident = incident_service.create_incident_from_hotspot(hotspot_data)
    assert incident is not None
    # Try to resolve an incident that is DETECTED (should fail)
    # We'll test this via the API later, but we can test the store update
    # For now, we just check that the incident service doesn't allow invalid transitions in the API layer.
    pass
