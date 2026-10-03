import { useState } from 'react';
import { Incident } from '@/lib/api';
import { acknowledgeIncident, resolveIncident } from '@/lib/api';

interface IncidentDetailProps {
  incident: Incident | null;
  onClose: () => void;
  onAcknowledge: (id: string) => Promise<void>;
  onResolve: (id: string) => Promise<void>;
  onAnalyze: (id: string) => Promise<void>;
  onRegenerate: (id: string) => Promise<void>;
  onViewOnMap: (latitude: number, longitude: number) => void;
}

export default function IncidentDetail({
  incident,
  onClose,
  onAcknowledge,
  onResolve,
  onAnalyze,
  onRegenerate,
  onViewOnMap
}: IncidentDetailProps) {
  const [analyses, setAnalyses] = useState<Record<string, any>>({}); // incident_id -> analysis
  const [loading, setLoading] = useState<Record<string, boolean>>({}); // incident_id -> boolean
  const [error, setError] = useState<Record<string, string>>({}); // incident_id -> error message

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
    } catch (err: unknown) {
      setError(prev => ({ ...prev, [id]: err instanceof Error ? err.message : String(err) }));
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
    } catch (err: unknown) {
      setError(prev => ({ ...prev, [id]: err instanceof Error ? err.message : String(err) }));
    } finally {
      setLoading(prev => ({ ...prev, [id]: false }));
    }
  };

  const analysis = analyses[incident?.id ?? ''];
  const isLoading = loading[incident?.id ?? ''];
  const err = error[incident?.id ?? ''];

  if (!incident) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">No incident selected</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="flex justify-between items-start px-6 py-4 border-b">
        <h2 className="text-xl font-bold text-gray-900">
          Incident Details
        </h2>
        <button
          onClick={onClose}
          className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
        >
          Close
        </button>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {/* Basic Incident Info */}
          <div className="space-y-2">
            <h3 className="font-medium text-gray-900">{incident.title}</h3>
            <div className="text-sm text-gray-500">
              {incident.region} • {
                incident.latitude != null && incident.longitude != null
                  ? `${incident.latitude.toFixed(4)}, ${incident.longitude.toFixed(4)}`
                  : 'Coordinates not available'
              }
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
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                {incident.source}
              </span>
            </div>
          </div>

          {/* Incident Metrics */}
          <div className="grid gap-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-sm font-medium text-gray-500">Risk Score</h4>
              <p className="text-2xl font-bold text-gray-900">{incident.risk_score}</p>
            </div>
            {incident.hotspot_confidence !== null && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-sm font-medium text-gray-500">Hotspot Confidence</h4>
                <p className="text-2xl font-bold text-gray-900">{incident.hotspot_confidence}%</p>
              </div>
            )}
            {incident.frp !== null && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-sm font-medium text-gray-500">FRP</h4>
                <p className="text-2xl font-bold text-gray-900">{incident.frp} MW</p>
              </div>
            )}
          </div>

          {/* Timestamps */}
          <div className="space-y-2">
            <p className="text-sm text-gray-500">
              Detected: {new Date(incident.detected_at).toLocaleString()}
            </p>
            {incident.acknowledged_at && (
              <p className="text-sm text-gray-500">
                Acknowledged: {new Date(incident.acknowledged_at).toLocaleString()}
              </p>
            )}
            {incident.resolved_at && (
              <p className="text-sm text-gray-500">
                Resolved: {new Date(incident.resolved_at).toLocaleString()}
              </p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            {incident.status === 'DETECTED' || incident.status === 'ACTIVE' && (
              <button
                onClick={() => onAcknowledge(incident.id)}
                className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
              >
                Acknowledge
              </button>
            )}
            {(incident.status === 'ACKNOWLEDGED' || incident.status === 'ACTIVE') && (
              <button
                onClick={() => onResolve(incident.id)}
                className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50"
              >
                Resolve
              </button>
            )}
            {incident.latitude !== null && incident.longitude !== null && (
              <button
                onClick={() => onViewOnMap(incident.latitude, incident.longitude)}
                className="px-3 py-1 bg-indigo-500 text-white text-sm rounded hover:bg-indigo-600"
              >
                View on Map
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
                    onClick={() => onAnalyze(incident.id)}
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                  >
                    ANALYZE WITH AI
                  </button>
                  {analysis && (
                    <button
                      onClick={() => onRegenerate(incident.id)}
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
      </div>
    </div>
  );
}