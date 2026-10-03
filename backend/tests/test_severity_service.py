import sys
sys.path.insert(0, '.')

from app.services.severity_service import SeverityService

def test_severity_service_initialization():
    service = SeverityService()
    assert service.risk_thresholds["LOW"] == 30
    assert service.risk_thresholds["MEDIUM"] == 60
    assert service.risk_thresholds["HIGH"] == 80
    assert service.risk_thresholds["CRITICAL"] == 100

def test_score_risk():
    service = SeverityService()
    assert service._score_risk(0) == "LOW"
    assert service._score_risk(30) == "LOW"
    assert service._score_risk(31) == "MEDIUM"
    assert service._score_risk(60) == "MEDIUM"
    assert service._score_risk(61) == "HIGH"
    assert service._score_risk(80) == "HIGH"
    assert service._score_risk(81) == "CRITICAL"
    assert service._score_risk(100) == "CRITICAL"

def test_score_confidence():
    service = SeverityService()
    assert service._score_confidence(None) == "LOW"
    assert service._score_confidence(0) == "LOW"
    assert service._score_confidence(30) == "LOW"
    assert service._score_confidence(31) == "MEDIUM"
    assert service._score_confidence(60) == "MEDIUM"
    assert service._score_confidence(61) == "HIGH"
    assert service._score_confidence(80) == "HIGH"
    assert service._score_confidence(81) == "CRITICAL"
    assert service._score_confidence(100) == "CRITICAL"

def test_score_frp():
    service = SeverityService()
    assert service._score_frp(None) == "LOW"
    assert service._score_frp(0) == "LOW"
    assert service._score_frp(10) == "LOW"
    assert service._score_frp(11) == "MEDIUM"
    assert service._score_frp(20) == "MEDIUM"
    assert service._score_frp(21) == "HIGH"
    assert service._score_frp(50) == "HIGH"
    assert service._score_frp(51) == "CRITICAL"
    assert service._score_frp(100) == "CRITICAL"

def test_determine_severity():
    service = SeverityService()
    # Only risk score
    assert service.determine_severity(risk_score=20) == "LOW"
    assert service.determine_severity(risk_score=50) == "MEDIUM"
    assert service.determine_severity(risk_score=90) == "CRITICAL"
    # Only confidence
    assert service.determine_severity(confidence=20) == "LOW"
    assert service.determine_severity(confidence=50) == "MEDIUM"
    assert service.determine_severity(confidence=90) == "CRITICAL"
    # Only FRP
    assert service.determine_severity(frp=5) == "LOW"
    assert service.determine_severity(frp=15) == "MEDIUM"
    assert service.determine_severity(frp=60) == "CRITICAL"
    # Multiple factors - take the highest
    assert service.determine_severity(risk_score=20, confidence=90) == "CRITICAL"
    assert service.determine_severity(risk_score=90, confidence=20) == "CRITICAL"
    assert service.determine_severity(risk_score=50, confidence=50, frp=50) == "HIGH"
    # No data
    assert service.determine_severity() == "LOW"
