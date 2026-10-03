"use client";

import { Alert } from '@/lib/api';
import { acknowledgeAlert, resolveAlert } from '@/lib/api';
import { useState } from 'react';

interface AlertPanelProps {
  alerts: Alert[];
}

const severityOrder: Record<string, number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
};

export default function AlertPanel({ alerts }: AlertPanelProps) {
  // #region agent log
  fetch('http://127.0.0.1:7654/ingest/e959db23-5300-44a8-9348-974f7876959a',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'27ea16'},body:JSON.stringify({sessionId:'27ea16',runId:'post-fix',hypothesisId:'B',location:'AlertPanel.tsx:render',message:'AlertPanel render entry',data:{hasUseClient:true,alertsCount:alerts?.length??0,hasOnClickHandlers:true},timestamp:Date.now()})}).catch(()=>{});
  // #endregion

  // Sort alerts: by severity (CRITICAL first), then by created_at descending (newest first)
  const sortedAlerts = [...alerts].sort((a, b) => {
    const severityDiff = (severityOrder[a.severity] ?? 999) - (severityOrder[b.severity] ?? 999);
    if (severityDiff !== 0) return severityDiff;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  // Take only the first 25 for display
  const displayedAlerts = sortedAlerts.slice(0, 25);

  const [analyses, setAnalyses] = useState<Record<string, any>>({}); // alert_id -> analysis
  const [loading, setLoading] = useState<Record<string, boolean>>({}); // alert_id -> boolean
  const [error, setError] = useState<Record<string, string>>({}); // alert_id -> error message

  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledgeAlert(id);
      window.location.reload();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      alert('Failed to acknowledge alert');
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveAlert(id);
      window.location.reload();
    } catch (error) {
      console.error('Error resolving alert:', error);
      alert('Failed to resolve alert');
    }
  };

  const handleAnalyze = async (id: string) => {
    setLoading((prev: Record<string, boolean>) => ({ ...prev, [id]: true }));
    setError((prev: Record<string, string>) => ({ ...prev, [id]: "" }));
    try {
      const response = await fetch(`/api/alerts/${id}/analyze`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to analyze alert: ${response.status}`);
      }
      const data = await response.json();
      setAnalyses((prev: Record<string, any>) => ({ ...prev, [id]: data.analysis }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      setError((prev: Record<string, string>) => ({ ...prev, [id]: message }));
    } finally {
      setLoading((prev: Record<string, boolean>) => ({ ...prev, [id]: false }));
    }
  };

  const handleRegenerate = async (id: string) => {
    setLoading((prev: Record<string, boolean>) => ({ ...prev, [id]: true }));
    setError((prev: Record<string, string>) => ({ ...prev, [id]: "" }));
    try {
      const response = await fetch(`/api/alerts/${id}/analyze/regenerate`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to regenerate analysis: ${response.status}`);
      }
      const data = await response.json();
      setAnalyses((prev: Record<string, any>) => ({ ...prev, [id]: data.analysis }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      setError((prev: Record<string, string>) => ({ ...prev, [id]: message }));
    } finally {
      setLoading((prev: Record<string, boolean>) => ({ ...prev, [id]: false }));
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">
          Alerts
        </h2>
      </div>
      <div className="px-6 py-4">
        {displayedAlerts.length === 0 ? (
          <p className="text-gray-500">No alerts</p>
        ) : (
          <div className="space-y-3">
            {displayedAlerts.map((alert) => {
              const analysis = analyses[alert.id];
              const isLoading = loading[alert.id];
              const err = error[alert.id];
              return (
                <div key={alert.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900">{alert.title}</h3>
                      <p className="text-sm text-gray-500">{alert.region}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          alert.severity === 'LOW'
                            ? 'bg-green-100 text-green-800'
                            : alert.severity === 'MEDIUM'
                            ? 'bg-yellow-100 text-yellow-800'
                            : alert.severity === 'HIGH'
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    <p>{alert.message}</p>
                    <p className="mt-1">Risk Score: {alert.risk_score}</p>
                    <p>Time: {new Date(alert.created_at).toLocaleString()}</p>
                  </div>
                  <div className="mt-3 flex items-center space-x-2">
                    {alert.status === 'NEW' && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
                      >
                        Acknowledge
                      </button>
                    )}
                    {alert.status === 'ACKNOWLEDGED' && (
                      <button
                        onClick={() => handleResolve(alert.id)}
                        className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                  {/* AI Analysis Section for Alerts */}
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
                          Analyzing alert...
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => handleAnalyze(alert.id)}
                            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                          >
                            ANALYZE WITH AI
                          </button>
                          {analysis && (
                            <button
                              onClick={() => handleRegenerate(alert.id)}
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