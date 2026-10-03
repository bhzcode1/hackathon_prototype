class SeverityService:
    """
    Service to determine fire severity based on risk score, hotspot confidence, and FRP.
    """

    def __init__(self):
        # Thresholds for risk score (0-100)
        self.risk_thresholds = {
            "LOW": 30,
            "MEDIUM": 60,
            "HIGH": 80,
            "CRITICAL": 100
        }
        # Thresholds for hotspot confidence (0-100)
        self.confidence_thresholds = {
            "LOW": 30,
            "MEDIUM": 60,
            "HIGH": 80,
            "CRITICAL": 100
        }
        # Thresholds for FRP (Fire Radiative Power) in MW
        # These are arbitrary for the hackathon
        self.frp_thresholds = {
            "LOW": 10,
            "MEDIUM": 20,
            "HIGH": 50,
            "CRITICAL": 100
        }

    def _score_risk(self, risk_score):
        """Convert risk score to a severity level based on thresholds."""
        if risk_score <= self.risk_thresholds["LOW"]:
            return "LOW"
        elif risk_score <= self.risk_thresholds["MEDIUM"]:
            return "MEDIUM"
        elif risk_score <= self.risk_thresholds["HIGH"]:
            return "HIGH"
        else:
            return "CRITICAL"

    def _score_confidence(self, confidence):
        """Convert hotspot confidence to a severity level."""
        if confidence is None:
            return "LOW"
        if confidence <= self.confidence_thresholds["LOW"]:
            return "LOW"
        elif confidence <= self.confidence_thresholds["MEDIUM"]:
            return "MEDIUM"
        elif confidence <= self.confidence_thresholds["HIGH"]:
            return "HIGH"
        else:
            return "CRITICAL"

    def _score_frp(self, frp):
        """Convert FRP to a severity level."""
        if frp is None:
            return "LOW"
        if frp <= self.frp_thresholds["LOW"]:
            return "LOW"
        elif frp <= self.frp_thresholds["MEDIUM"]:
            return "MEDIUM"
        elif frp <= self.frp_thresholds["HIGH"]:
            return "HIGH"
        else:
            return "CRITICAL"

    def determine_severity(self, risk_score=None, confidence=None, frp=None):
        """
        Determine overall severity from risk score, hotspot confidence, and FRP.
        We take the highest severity from the three factors.
        """
        severities = []

        if risk_score is not None:
            severities.append(self._score_risk(risk_score))
        if confidence is not None:
            severities.append(self._score_confidence(confidence))
        if frp is not None:
            severities.append(self._score_frp(frp))

        # If no data, default to LOW
        if not severities:
            return "LOW"

        # Order of severity: LOW < MEDIUM < HIGH < CRITICAL
        severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        # Find the highest severity
        highest = max(severities, key=lambda s: severity_order.index(s))
        return highest
