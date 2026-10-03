'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Incident,
  Alert,
  RiskData,
  HotspotData,
  fetchRiskData,
  fetchHotspotsData,
  fetchIncidentsData,
  fetchAlertsData,
  acknowledgeIncident,
  resolveIncident,
} from '@/lib/api';
import Header from '@/components/Header';
import FireMapWrapper from '@/components/FireMapWrapper';
import ActiveIncidents from '@/components/ActiveIncidents';
import AlertPanel from '@/components/AlertPanel';
import IncidentDetail from '@/components/IncidentDetail';

const SEVERITY_ORDER: Record<string, number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
const REFRESH_MS = 5 * 60 * 1000;

function sortBySeverityThenDate<T extends { severity: string }>(
  items: T[],
  getDate: (item: T) => string
): T[] {
  return [...items].sort((a, b) => {
    const diff = (SEVERITY_ORDER[a.severity] ?? 999) - (SEVERITY_ORDER[b.severity] ?? 999);
    if (diff !== 0) return diff;
    return new Date(getDate(b)).getTime() - new Date(getDate(a)).getTime();
  });
}

export default function Home() {
  const [riskData, setRiskData] = useState<RiskData[]>([]);
  const [hotspotsData, setHotspotsData] = useState<HotspotData[]>([]);
  const [incidentsData, setIncidentsData] = useState<Incident[]>([]);
  const [alertsData, setAlertsData] = useState<Alert[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number] | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [hadError, setHadError] = useState(false);

  const fetchAllData = useCallback(async () => {
    setRefreshing(true);
    const [risk, hotspots, incidents, alerts] = await Promise.allSettled([
      fetchRiskData(),
      fetchHotspotsData(),
      fetchIncidentsData(),
      fetchAlertsData(),
    ]);

    // Only overwrite state on success so a failed poll keeps the last good data
    if (risk.status === 'fulfilled') setRiskData(risk.value);
    else console.error('Error fetching risk data:', risk.reason);

    if (hotspots.status === 'fulfilled') setHotspotsData(hotspots.value);
    else console.error('Error fetching hotspots data:', hotspots.reason);

    if (incidents.status === 'fulfilled') setIncidentsData(incidents.value);
    else console.error('Error fetching incidents data:', incidents.reason);

    if (alerts.status === 'fulfilled') setAlertsData(alerts.value);
    else console.error('Error fetching alerts data:', alerts.reason);

    setHadError([risk, hotspots, incidents, alerts].every(r => r.status === 'rejected'));
    setLastUpdated(new Date().toLocaleString());
    setRefreshing(false);
  }, []);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, REFRESH_MS);
    return () => clearInterval(interval);
  }, [fetchAllData]);

  // Derived data
  const selectedIncident = useMemo(
    () => incidentsData.find(i => i.id === selectedIncidentId) ?? null,
    [incidentsData, selectedIncidentId]
  );

  const displayedIncidents = useMemo(
    () => sortBySeverityThenDate(incidentsData, i => i.detected_at).slice(0, 25),
    [incidentsData]
  );
  const displayedAlerts = useMemo(
    () => sortBySeverityThenDate(alertsData, a => a.created_at).slice(0, 25),
    [alertsData]
  );

  const totalRegions = riskData.length;
  const activeHotspots = hotspotsData.length;
  const activeAlerts = alertsData.filter(a => a.status === 'NEW' || a.status === 'ACKNOWLEDGED').length;
  const activeIncidents = incidentsData.filter(i =>
    ['DETECTED', 'ACTIVE', 'ACKNOWLEDGED'].includes(i.status)
  ).length;
  const criticalIncidents = incidentsData.filter(i => i.severity === 'CRITICAL').length;
  const highRiskZones = riskData.filter(r => r.risk_level === 'HIGH' || r.risk_level === 'CRITICAL').length;

  // Handlers
  const updateIncident = (id: string, patch: Partial<Incident>) =>
    setIncidentsData(prev => prev.map(inc => (inc.id === id ? { ...inc, ...patch } : inc)));

  const callAnalysisEndpoint = async (id: string, path: string, label: string) => {
    try {
      const res = await fetch(`/api/incidents/${id}/${path}`, { method: 'POST' });
      if (!res.ok) throw new Error(`Failed to ${label}: ${res.status}`);
      updateIncident(id, await res.json());
    } catch (error) {
      console.error(`Error trying to ${label}:`, error);
    }
  };

  const handleAcknowledge = async (id: string) => {
    await acknowledgeIncident(id);
    await fetchAllData();
  };
  const handleResolve = async (id: string) => {
    await resolveIncident(id);
    await fetchAllData();
  };

  const kpis = [
    { label: 'MONITORED REGIONS', value: totalRegions, border: '', text: 'text-gray-900' },
    { label: 'ACTIVE INCIDENTS', value: activeIncidents, border: 'border-l-4 border-blue-500', text: 'text-blue-600' },
    { label: 'CRITICAL INCIDENTS', value: criticalIncidents, border: 'border-l-4 border-red-500', text: 'text-red-600' },
    { label: 'ACTIVE ALERTS', value: activeAlerts, border: 'border-l-4 border-purple-500', text: 'text-purple-600' },
    { label: 'SATELLITE HOTSPOTS', value: activeHotspots, border: 'border-l-4 border-orange-500', text: 'text-orange-600' },
    { label: 'HIGH-RISK ZONES', value: highRiskZones, border: 'border-l-4 border-yellow-500', text: 'text-yellow-600' },
  ];

  const initialLoading = refreshing && lastUpdated === null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="px-6 py-4">
        {/* Title + refresh */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">FireSight AI Command Center</h1>
            <p className="text-sm text-gray-500">Real-time emergency monitoring & response system</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-500">Last updated: {lastUpdated ?? 'Never'}</div>
            <button
              onClick={fetchAllData}
              disabled={refreshing}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {initialLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto" />
            <p className="mt-4 text-sm text-gray-500">Loading initial data...</p>
          </div>
        )}

        {hadError && !refreshing && (
          <div className="text-center py-6 mb-6 bg-white rounded-lg shadow">
            <p className="text-sm text-gray-500 mb-3">
              Unable to load data. Please check your connection and try again.
            </p>
            <button
              onClick={fetchAllData}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Try Again
            </button>
          </div>
        )}

        {/* KPI row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          {kpis.map(k => (
            <div key={k.label} className={`bg-white rounded-lg shadow p-4 ${k.border}`}>
              <h3 className="text-sm font-medium text-gray-500">{k.label}</h3>
              <p className={`text-2xl font-bold mt-2 ${k.text}`}>{k.value}</p>
            </div>
          ))}
        </div>

        {/* Map + side panels: stacked on mobile, 2/3 + 1/3 on desktop */}
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <div className="bg-white rounded-lg shadow h-[500px] relative">
              <FireMapWrapper hotspotsData={hotspotsData} center={mapCenter} />
              {hotspotsData.length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <p className="text-sm text-gray-500 bg-white/80 px-3 py-1 rounded">
                    No satellite hotspot data available
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="md:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow">
              {displayedIncidents.length === 0 ? (
                <div className="px-6 py-4">
                  <p className="text-sm text-gray-500">No active incidents detected</p>
                </div>
              ) : (
                <ActiveIncidents
                  incidents={displayedIncidents}
                  onIncidentSelect={(id: string) => setSelectedIncidentId(id)}
                  selectedIncidentId={selectedIncidentId}
                />
              )}
            </div>

            <div className="bg-white rounded-lg shadow">
              {displayedAlerts.length === 0 ? (
                <div className="px-6 py-4">
                  <p className="text-sm text-gray-500">No active alerts</p>
                </div>
              ) : (
                <AlertPanel alerts={displayedAlerts} />
              )}
            </div>
          </div>
        </div>

        {/* Selected incident detail */}
        {selectedIncident && (
          <div className="mt-6">
            <IncidentDetail
              incident={selectedIncident}
              onClose={() => setSelectedIncidentId(null)}
              onAcknowledge={handleAcknowledge}
              onResolve={handleResolve}
              onAnalyze={(id: string) => callAnalysisEndpoint(id, 'analyze', 'analyze incident')}
              onRegenerate={(id: string) =>
                callAnalysisEndpoint(id, 'analyze/regenerate', 'regenerate analysis')
              }
              onViewOnMap={(lat: number, lng: number) => setMapCenter([lat, lng])}
            />
          </div>
        )}
      </main>
    </div>
  );
}