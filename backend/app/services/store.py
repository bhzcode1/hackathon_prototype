class InMemoryStore:
    def __init__(self):
        self.incidents = {}  # id -> incident
        self.alerts = {}     # id -> alert
        self.incident_id_counter = 0
        self.alert_id_counter = 0

    def create_incident(self, incident_data):
        self.incident_id_counter += 1
        incident_id = str(self.incident_id_counter)
        incident = {
            "id": incident_id,
            **incident_data,
            "analysis": None  # Initialize analysis as None
        }
        self.incidents[incident_id] = incident
        return incident

    def get_incident(self, incident_id):
        return self.incidents.get(incident_id)

    def get_incidents(self):
        return list(self.incidents.values())

    def update_incident(self, incident_id, update_data):
        if incident_id in self.incidents:
            self.incidents[incident_id].update(update_data)
            return self.incidents[incident_id]
        return None

    def delete_incident(self, incident_id):
        if incident_id in self.incidents:
            del self.incidents[incident_id]
            return True
        return False

    def set_incident_analysis(self, incident_id, analysis):
        """
        Set or update the AI analysis for an incident.
        """
        if incident_id in self.incidents:
            self.incidents[incident_id]["analysis"] = analysis
            return True
        return False

    def get_incident_analysis(self, incident_id):
        """
        Get the AI analysis for an incident, if it exists.
        """
        incident = self.incidents.get(incident_id)
        if incident:
            return incident.get("analysis")
        return None

    def create_alert(self, alert_data):
        self.alert_id_counter += 1
        alert_id = str(self.alert_id_counter)
        alert = {
            "id": alert_id,
            **alert_data,
            "analysis": None  # Initialize analysis as None for alerts too, though not used yet
        }
        self.alerts[alert_id] = alert
        return alert

    def get_alert(self, alert_id):
        return self.alerts.get(alert_id)

    def get_alerts(self):
        return list(self.alerts.values())

    def update_alert(self, alert_id, update_data):
        if alert_id in self.alerts:
            self.alerts[alert_id].update(update_data)
            return self.alerts[alert_id]
        return None

    def delete_alert(self, alert_id):
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return True
        return False

    def set_alert_analysis(self, alert_id, analysis):
        """
        Set or update the AI analysis for an alert.
        """
        if alert_id in self.alerts:
            self.alerts[alert_id]["analysis"] = analysis
            return True
        return False

    def get_alert_analysis(self, alert_id):
        """
        Get the AI analysis for an alert, if it exists.
        """
        alert = self.alerts.get(alert_id)
        if alert:
            return alert.get("analysis")
        return None

# Singleton instance
store = InMemoryStore()