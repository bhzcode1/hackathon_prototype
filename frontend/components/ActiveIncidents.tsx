"use client";

import { Incident } from '@/lib/api';
import { acknowledgeIncident, resolveIncident } from '@/lib/api';
import { useState } from 'react';

interface ActiveIncidentsProps {
  incidents: Incident[];
  onIncidentSelect?: (id: string) => void;
  selectedIncidentId?: string | null;
}

const severityOrder: Record<string, number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
};

export default function ActiveIncidents({ incidents, selectedIncidentId, onIncidentSelect }: ActiveIncidentsProps) {
  // #region agent log
  fetch('http://127.0.0.1:7654/ingest/e959db23-5300-44a8-9348-974f7876959a',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'27ea16'},body:JSON.stringify({sessionId:'27ea16',runId:'post-fix',hypothesisId:'A',location:'ActiveIncidents.tsx:render',message:'ActiveIncidents render entry',data:{hasUseClient:true,incidentsCount:incidents?.length??0,hasOnClickHandlers:true},timestamp:Date.now()})}).catch(()=>{});
  // #endregion

  // Sort incidents: by severity (CRITICAL first), then by detected_at descending (newest first)
  const sortedIncidents = [...incidents].sort((a, b) => {
    const severityDiff = (severityOrder[a.severity] ?? 999) - (severityOrder[b.severity] ?? 999);
    if (severityDiff !== 0) return severityDiff;
    return new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime();
  });

  // Take only the first 25 for display
  const displayedIncidents = sortedIncidents.slice(0, 25);

  const [analyses, setAnalyses] = useState<Record<string, any>>({}); // incident_id -> analysis
  const [loading, setLoading] = useState<Record<string, boolean>>({}); // incident_id -> boolean
  const [error, setError] = useState<Record<string, string>>({}); // incident_id -> error message

  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledgeIncident(id);
      window.location.reload();
    } catch (error) {
      console.error('Error acknowledging incident:', error);
      alert('Failed to acknowledge incident');
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveIncident(id);
      window.location.reload();
    } catch (error) {
      console.error('Error resolving incident:', error);
      alert('Failed to resolve incident');
    }
  };

  const handleAnalyze = async (id: string) => {
    setLoading(prev => ({ ...prev, [id]: true }));
    setError(prev => ({ ...prev, [id]: "" }));
    try {
      const response = await fetch(`/api/incidents/${id}/analyze`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to analyze incident: ${response.status}`);
      }
      const data = await response.json();
      setAnalyses(prev => ({ ...prev, [id]: data.analysis }));
    } catch (err) {
      setError(prev => ({ ...prev, [id]: err.message }));
    } finally {
      setLoading(prev => ({ ...prev, [id]: false }));
    }
  };

  const handleRegenerate = async (id: string) => {
    setLoading(prev => ({ ...prev, [id]: true }));
    setError(prev => ({ ...prev, [id]: "" }));
    try {
      const response = await fetch(`/api/incidents/${id}/analyze/regenerate`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to regenerate analysis: ${response.status}`);
      }
      const data = await response.json();
      setAnalyses(prev => ({ ...prev, [id]: data.analysis }));
    } catch (err) {
      setError(prev => ({ ...prev, [id]: err.message }));
    } finally {
      setLoading(prev => ({ ...prev, [id]: false }));
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">
            Active Incidents
          </h2>
          <p className="text-xs text-gray-500">
            Showing up to 25 highest-priority incidents
          </p>
        </div>
      </div>
      <div className="px-6 py-4">
        {displayedIncidents.length === 0 ? (
          <p className="text-gray-500">No active incidents</p>
        ) : (
          <div className="space-y-3">
            {displayedIncidents.map((incident) => {
              const isDetectedOrActive = incident.status === 'DETECTED' || incident.status === 'ACTIVE';
              const isAcknowledged = incident.status === 'ACKNOWLEDGED';
              const analysis = analyses[incident.id];
              const isLoading = loading[incident.id];
              const err = error[incident.id];
              return (
                <div
                key={incident.id}
                className={`
                  border rounded-lg p-4
                  ${selectedIncidentId && incident.id === selectedIncidentId ? 'ring-2 ring-blue-500' : ''}
                  cursor-pointer
                  hover:bg-gray-50
                `}
                onClick={() => {
                  if (onIncidentSelect) {
                    onIncidentSelect(incident.id);
                  }
                }}
              >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900">{incident.title}</h3>
                      <p className="text-sm text-gray-500">
                        {incident.region} • {
                          incident.latitude != null && incident.longitude != null
                            ? `${incident.latitude.toFixed(4)}, ${incident.longitude.toFixed(4)}`
                            : 'Coordinates not available'
                        }
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          incident.severity === 'LOW'
                            ? 'bg-green-100 text-green-800'
                            : incident.severity === 'MEDIUM'
                            ? 'bg-yellow-100 text-yellow-800'
                            : incident.severity === 'HIGH'
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {incident.severity}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    <p>Risk Score: {incident.risk_score}</p>
                    {incident.hotspot_confidence !== null && (
                      <p>Hotspot Confidence: {incident.hotspot_confidence}%</p>
                    )}
                    {incident.frp !== null && (
                      <p>FRP: {incident.frp} MW</p>
                    )}
                    <p>Detected: {new Date(incident.detected_at).toLocaleString()}</p>
                    {incident.acknowledged_at && (
                      <p>Acknowledged: {new Date(incident.acknowledged_at).toLocaleString()}</p>
                    )}
                    {incident.resolved_at && (
                      <p>Resolved: {new Date(incident.resolved_at).toLocaleString()}</p>
                    )}
                  </div>
                  <div className="mt-3 flex items-center space-x-2">
                    {isDetectedOrActive && (
                      <button
                        onClick={() => handleAcknowledge(incident.id)}
                        className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
                      >
                        Acknowledge
                      </button>
                    )}
                    {isAcknowledged && (
                      <button
                        onClick={() => handleResolve(incident.id)}
                        className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                  {/* AI Analysis Section */}
                  {analysis ? (
                    <div className="mt-4 pt-3 border-t">
                      <h3 className="font-medium text-gray-900">AI Incident Intelligence</h3>
                      <div className="mt-2 space-y-2">
                        <div className="text-sm font-medium text-gray-700">Summary:</div>
                        <p className="text-gray-600">{analysis.summary}</p>
                        <div className="text-sm font-medium text-gray-700">Risk Explanation:</div>
                        <p className="text-gray-600">{analysis.risk_explanation}</p>
                        <div className="text-sm font-medium text-gray-700">Key Factors:</div>
                        <ul className="list-disc list-inside text-gray-600 mt-1">
                          {analysis.key_factors.map((factor: string, index: number) => (
                            <li key={index}>{factor}</li>
                          ))}
                        </ul>
                        <div className="text-sm font-medium text-gray-700">Recommended Actions:</div>
                        <ul className="list-disc list-inside text-gray-600 mt-1">
                          {analysis.recommended_actions.map((action: string, index: number) => (
                            <li key={index}>{action}</li>
                          ))}
                        </ul>
                        <div className="text-sm font-medium text-gray-700">Limitations:</div>
                        <p className="text-gray-600">{analysis.limitations}</p>
                        <div className="text-xs text-gray-500 mt-2">
                          Provider: {analysis.provider}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-3">
                      {isLoading ? (
                        <button
                          disabled
                          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                        >
                          Analyzing incident...
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => handleAnalyze(incident.id)}
                            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                          >
                            ANALYZE WITH AI
                          </button>
                          {analysis && (
                            <button
                              onClick={() => handleRegenerate(incident.id)}
                              className="ml-2 px-3 py-1 bg-yellow-500 text-white text-sm rounded hover:bg-yellow-600"
                            >
                              REGENERATE ANALYSIS
                            </button>
                          )}
                        </>
                      )}
                      {err && (
                        <p className="mt-2 text-sm text-red-500">Error: {err}</p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}