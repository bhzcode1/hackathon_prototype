from app.services.store import store
from app.services.severity_service import SeverityService
from app.schemas.incidents import IncidentCreate
from datetime import datetime

class IncidentDetectionService:
    def __init__(self):
        self.severity_service = SeverityService()

    def _generate_title(self, region, severity, source):
        """Generate a title for the incident."""
        if source == "NASA FIRMS":
            return f"{severity} Fire Hotspot Detected in {region}"
        else:
            return f"{severity} Fire Risk Detected in {region}"

    def create_incident_from_hotspot(self, hotspot_data):
        """
        Create an incident from a NASA FIRMS hotspot.
        Returns the incident if created, None if duplicate.
        """
        # We'll use a rounded version to create an ID.
        lat = round(hotspot_data.get("latitude", 0), 3)
        lon = round(hotspot_data.get("longitude", 0), 3)
        hotspot_id = f"{lat}_{lon}"

        # Check if an incident already exists for this hotspot_id
        for incident in store.incidents.values():
            if incident.get("hotspot_id") == hotspot_id:
                # Duplicate found
                return None

        # Determine severity
        severity = self.severity_service.determine_severity(
            risk_score=None,  # We don't have risk score from hotspot alone
            confidence=hotspot_data.get("confidence"),
            frp=hotspot_data.get("frp")
        )

        # Prepare incident data
        incident_data = {
            "title": self._generate_title(hotspot_data.get("region", "Unknown"), severity, hotspot_data.get("source", "NASA FIRMS")),
            "region": hotspot_data.get("region", "Unknown"),
            "latitude": hotspot_data.get("latitude"),
            "longitude": hotspot_data.get("longitude"),
            "risk_score": 0,  # We don't have risk score from hotspot alone
            "risk_level": "LOW",  # Default
            "hotspot_id": hotspot_id,
            "hotspot_confidence": hotspot_data.get("confidence"),
            "frp": hotspot_data.get("frp"),
            "severity": severity,
            "source": hotspot_data.get("source", "NASA FIRMS"),
            "status": "DETECTED",
            "detected_at": datetime.utcnow(),
        }

        # Create incident
        incident = store.create_incident(incident_data)
        return incident

    def create_incident_from_risk(self, risk_data, lat, lon):
        """
        Create an incident from a high-risk zone prediction.
        Returns the incident if created, None if not appropriate or duplicate.
        """
        # We'll create an incident only if the risk is HIGH or CRITICAL
        risk_score = risk_data.get("risk_score", 0)
        if risk_score < 60:  # Only MEDIUM and above? Actually, we want HIGH and CRITICAL
            return None

        # For risk-based incidents, we don't have a hotspot_id, so we use a generated ID based on location
        # We'll round the latitude and longitude to create an ID.
        lat_rounded = round(lat, 3)
        lon_rounded = round(lon, 3)
        hotspot_id = f"risk_{lat_rounded}_{lon_rounded}"  # Prefix to distinguish from hotspot incidents

        # Check for duplicate risk-based incident at the same location
        for incident in store.incidents.values():
            if incident.get("hotspot_id") == hotspot_id:
                return None

        # Determine severity from risk score (we don't have hotspot data)
        severity = self.severity_service.determine_severity(
            risk_score=risk_score,
            confidence=None,
            frp=None
        )

        incident_data = {
            "title": self._generate_title(risk_data.get("region", "Unknown"), severity, "FireSight Prediction"),
            "region": risk_data.get("region", "Unknown"),
            "latitude": lat,
            "longitude": lon,
            "risk_score": risk_score,
            "risk_level": risk_data.get("risk_level", "LOW"),
            "hotspot_id": hotspot_id,
            "hotspot_confidence": None,
            "frp": None,
            "severity": severity,
            "source": "FireSight Prediction",
            "status": "DETECTED",
            "detected_at": datetime.utcnow(),
        }

        incident = store.create_incident(incident_data)
        return incident

    def process_hotspot(self, hotspot_data):
        """
        Process a single hotspot: create incident if needed, then generate alert.
        """
        incident = self.create_incident_from_hotspot(hotspot_data)
        if incident:
            # Generate alert for the incident
            alert_service.create_alert_for_incident(incident)
        return incident

    def process_risk_zone(self, risk_data, lat, lon):
        """
        Process a risk zone: create incident if needed, then generate alert.
        """
        incident = self.create_incident_from_risk(risk_data, lat, lon)
        if incident:
            alert_service.create_alert_for_incident(incident)
        return incident

# We'll create a singleton instance
incident_service = IncidentDetectionService()

# Set the alert service instance (to avoid circular import issues)
from app.services.alert_service import alert_service
incident_service.alert_service = alert_service
