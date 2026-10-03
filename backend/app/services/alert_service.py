from app.services.store import store
from app.schemas.alerts import AlertCreate
from datetime import datetime

class AlertService:
    def __init__(self):
        pass

    def _generate_message(self, incident):
        """Generate a human-readable message for the alert."""
        severity = incident["severity"]
        region = incident["region"]
        source = incident["source"]

        if source == "NASA FIRMS":
            confidence = incident.get("hotspot_confidence")
            frp = incident.get("frp")
            msg = f"{severity} fire risk detected near {region}. "
            if confidence is not None:
                msg += f"Satellite hotspot confidence is {confidence}%. "
            if frp is not None:
                msg += f"FRP is {frp} MW. "
            msg = msg.strip()
            if not msg.endswith("."):
                msg += "."
        else:
            risk_score = incident["risk_score"]
            msg = f"{severity} fire risk predicted in {region} with a risk score of {risk_score}."
        return msg

    def create_alert_for_incident(self, incident):
        """
        Create an alert for a given incident.
        """
        alert_type = "HOTSPOT_DETECTED" if incident["source"] == "NASA FIRMS" else "HIGH_FIRE_RISK"
        if incident["severity"] == "CRITICAL":
            alert_type = "CRITICAL_FIRE_RISK"

        try:
            risk_score = int(round(float(incident.get("risk_score", 0))))
        except (TypeError, ValueError):
            risk_score = 0

        alert_data = {
            "incident_id": str(incident["id"]),
            "alert_type": alert_type,
            "title": incident["title"],
            "message": self._generate_message(incident),
            "severity": incident["severity"],
            "region": incident["region"],
            "risk_score": risk_score,
            "source": incident["source"],
            "status": "NEW",
            "created_at": datetime.utcnow().isoformat(),
        }

        alert = store.create_alert(alert_data)
        return alert

# Singleton instance
alert_service = AlertService()
