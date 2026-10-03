export interface Incident {
  id: string;
  title: string;
  region: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: string;
  hotspot_id: string | null;
  hotspot_confidence: number | null;
  frp: number | null;
  severity: string;
  source: string;
  status: string; // DETECTED, ACTIVE, ACKNOWLEDGED, RESOLVED
  detected_at: string; // ISO string
  acknowledged_at: string | null;
  resolved_at: string | null;
}

export interface Alert {
  id: string;
  incident_id: string;
  alert_type: string; // HOTSPOT_DETECTED, HIGH_FIRE_RISK, CRITICAL_FIRE_RISK
  title: string;
  message: string;
  severity: string;
  region: string;
  risk_score: number;
  source: string; // NASA FIRMS or FireSight Prediction
  status: string; // NEW, ACKNOWLEDGED, RESOLVED
  created_at: string; // ISO string
}

export interface RiskData {
  region: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  rainfall: number;
}

export interface HotspotData {
  latitude: number;
  longitude: number;
  acq_date: string;
  acq_time: string;
  satellite: string;
  instrument: string;
  confidence: number | null;
  frp: number | null;
  daynight: string;
  severity: string;
  source: string;
  detected_at: string;
}

export interface GridRiskData {
  id: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  rainfall: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const fetchRiskData = async (): Promise<RiskData[]> => {
  const response = await fetch(`${API_BASE_URL}/api/risk`);
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to fetch risk data: ${response.status} ${response.statusText} - ${response.url} - ${errorBody}`);
  }
  return response.json();
};

export const fetchRiskZones = async (): Promise<GridRiskData[]> => {
  const response = await fetch(`${API_BASE_URL}/api/risk/zones`);
  if (!response.ok) {
    throw new Error('Failed to fetch risk zones data');
  }
  return response.json();
};

export const fetchHotspotsData = async (): Promise<HotspotData[]> => {
  const response = await fetch(`${API_BASE_URL}/api/hotspots`);
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to fetch hotspots data: ${response.status} ${response.statusText} - ${response.url} - ${errorBody}`);
  }
  return response.json();
};

export const fetchIncidentsData = async (): Promise<Incident[]> => {
  const response = await fetch(`${API_BASE_URL}/api/incidents`);
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to fetch incidents data: ${response.status} ${response.statusText} - ${response.url} - ${errorBody}`);
  }
  return response.json();
};

export const fetchAlertsData = async (): Promise<Alert[]> => {
  const response = await fetch(`${API_BASE_URL}/api/alerts`);
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to fetch alerts data: ${response.status} ${response.statusText} - ${response.url} - ${errorBody}`);
  }
  return response.json();
};

// New functions for acknowledging and resolving incidents and alerts
export const acknowledgeIncident = async (incidentId: string): Promise<Incident> => {
  const response = await fetch(`${API_BASE_URL}/api/incidents/${incidentId}/acknowledge`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to acknowledge incident');
  }
  return response.json();
};

export const resolveIncident = async (incidentId: string): Promise<Incident> => {
  const response = await fetch(`${API_BASE_URL}/api/incidents/${incidentId}/resolve`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to resolve incident');
  }
  return response.json();
};

export const acknowledgeAlert = async (alertId: string): Promise<Alert> => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/${alertId}/acknowledge`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to acknowledge alert');
  }
  return response.json();
};

export const resolveAlert = async (alertId: string): Promise<Alert> => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/${alertId}/resolve`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to resolve alert');
  }
  return response.json();
};
