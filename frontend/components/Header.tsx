import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Header() {
  const [systemHealth, setSystemHealth] = useState({
    backend: "Checking...",
    ml_engine: "Checking...",
    nasa_firms: "Checking...",
    ai_engine: "Checking..."
  });

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await fetch('/api/health/detailed');
        if (response.ok) {
          const data = await response.json();
          setSystemHealth(data.services || {
            backend: "Unknown",
            ml_engine: "Unknown",
            nasa_firms: "Unknown",
            ai_engine: "Unknown"
          });
        } else {
          setSystemHealth({
            backend: "Error",
            ml_engine: "Error",
            nasa_firms: "Error",
            ai_engine: "Error"
          });
        }
      } catch (error) {
        console.error('Failed to fetch system health:', error);
        setSystemHealth({
          backend: "Error",
          ml_engine: "Error",
          nasa_firms: "Error",
          ai_engine: "Error"
        });
      }
    };

    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex items-center space-x-4 mb-4 md:mb-0">
            <div className="flex-shrink-0">
              <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                FireSight AI
              </h1>
              <p className="text-sm text-gray-500">
                Emergency Monitoring Command Center
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="space-x-2">
              <div className="flex items-center">
                <span className="mr-1">Backend:</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  systemHealth.backend === 'ONLINE' ? 'bg-green-100 text-green-800' :
                  systemHealth.backend === 'OFFLINE' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {systemHealth.backend}
                </span>
              </div>
              <div className="flex items-center">
                <span className="mr-1">ML Engine:</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  systemHealth.ml_engine === 'ONLINE' ? 'bg-green-100 text-green-800' :
                  systemHealth.ml_engine === 'OFFLINE' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {systemHealth.ml_engine}
                </span>
              </div>
              <div className="flex items-center">
                <span className="mr-1">NASA FIRMS:</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  systemHealth.nasa_firms === 'ONLINE' ? 'bg-green-100 text-green-800' :
                  systemHealth.nasa_firms === 'OFFLINE' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {systemHealth.nasa_firms}
                </span>
              </div>
              <div className="flex items-center">
                <span className="mr-1">AI Engine:</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  systemHealth.ai_engine === 'ONLINE (RULE-BASED)' || systemHealth.ai_engine === 'ONLINE' ? 'bg-green-100 text-green-800' :
                  systemHealth.ai_engine === 'OFFLINE' || systemHealth.ai_engine === 'OFFLINE (NO API KEY)' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {systemHealth.ai_engine}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}