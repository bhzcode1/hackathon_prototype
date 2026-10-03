import sys
sys.path.insert(0, '.')

from app.services.store import store

def clear_store():
    store.incidents.clear()
    store.alerts.clear()
    store.incident_id_counter = 0
    store.alert_id_counter = 0

def test_store_initialization():
    clear_store()
    assert store.incidents == {}
    assert store.alerts == {}
    assert store.incident_id_counter == 0
    assert store.alert_id_counter == 0

def test_create_incident():
    clear_store()
    incident_data = {
        "title": "Test Incident",
        "region": "Test Region",
        "latitude": 10.0,
        "longitude": 20.0,
        "risk_score": 50,
        "risk_level": "MEDIUM",
        "hotspot_id": "test_1",
        "hotspot_confidence": 80.0,
        "frp": 10.0,
        "severity": "MEDIUM",
        "source": "Test",
        "status": "DETECTED",
        "detected_at": "2026-10-02T00:00:00Z",
    }
    incident = store.create_incident(incident_data)
    assert incident["id"] == "1"
    assert incident["title"] == "Test Incident"
    assert store.get_incident("1") == incident

def test_get_incidents():
    clear_store()
    incidents = store.get_incidents()
    assert len(incidents) == 0

def test_update_incident():
    clear_store()
    incident_data = {
        "title": "Test Incident",
        "region": "Test Region",
        "latitude": 10.0,
        "longitude": 20.0,
        "risk_score": 50,
        "risk_level": "MEDIUM",
        "hotspot_id": "test_1",
        "hotspot_confidence": 80.0,
        "frp": 10.0,
        "severity": "MEDIUM",
        "source": "Test",
        "status": "DETECTED",
        "detected_at": "2026-10-02T00:00:00Z",
    }
    store.create_incident(incident_data)
    updated = store.update_incident("1", {"status": "ACKNOWLEDGED"})
    assert updated["status"] == "ACKNOWLEDGED"
    assert store.get_incident("1")["status"] == "ACKNOWLEDGED"

def test_create_alert():
    clear_store()
    alert_data = {
        "incident_id": "1",
        "type": "HOTSPOT_DETECTED",
        "title": "Test Alert",
        "message": "Test message",
        "severity": "MEDIUM",
        "region": "Test Region",
        "risk_score": 50,
        "status": "NEW",
        "created_at": "2026-10-02T00:00:00Z",
    }
    alert = store.create_alert(alert_data)
    assert alert["id"] == "1"
    assert alert["title"] == "Test Alert"
    assert store.get_alert("1") == alert

def test_get_alerts():
    clear_store()
    alerts = store.get_alerts()
    assert len(alerts) == 0

def test_update_alert():
    clear_store()
    alert_data = {
        "incident_id": "1",
        "type": "HOTSPOT_DETECTED",
        "title": "Test Alert",
        "message": "Test message",
        "severity": "MEDIUM",
        "region": "Test Region",
        "risk_score": 50,
        "status": "NEW",
        "created_at": "2026-10-02T00:00:00Z",
    }
    store.create_alert(alert_data)
    updated = store.update_alert("1", {"status": "ACKNOWLEDGED"})
    assert updated["status"] == "ACKNOWLEDGED"
    assert store.get_alert("1")["status"] == "ACKNOWLEDGED"

def test_delete_incident():
    clear_store()
    incident_data = {
        "title": "Test Incident",
        "region": "Test Region",
        "latitude": 10.0,
        "longitude": 20.0,
        "risk_score": 50,
        "risk_level": "MEDIUM",
        "hotspot_id": "test_1",
        "hotspot_confidence": 80.0,
        "frp": 10.0,
        "severity": "MEDIUM",
        "source": "Test",
        "status": "DETECTED",
        "detected_at": "2026-10-02T00:00:00Z",
    }
    store.create_incident(incident_data)
    assert store.delete_incident("1") == True
    assert store.get_incident("1") is None

def test_delete_alert():
    clear_store()
    alert_data = {
        "incident_id": "1",
        "type": "HOTSPOT_DETECTED",
        "title": "Test Alert",
        "message": "Test message",
        "severity": "MEDIUM",
        "region": "Test Region",
        "risk_score": 50,
        "status": "NEW",
        "created_at": "2026-10-02T00:00:00Z",
    }
    store.create_alert(alert_data)
    assert store.delete_alert("1") == True
    assert store.get_alert("1") is None
