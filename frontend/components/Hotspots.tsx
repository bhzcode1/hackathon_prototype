import { HotspotData } from '@/lib/api';

interface HotspotsProps {
  hotspotsData: HotspotData[];
}

export default function Hotspots({ hotspotsData }: HotspotsProps) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">
          Active Hotspots
        </h2>
        <div className="flex items-center space-x-2 text-sm">
          {hotspotsData.length > 0 && hotspotsData[0].source === "NASA FIRMS" ? (
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
              LIVE SATELLITE DATA
            </span>
          ) : (
            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
              DEMO DATA
            </span>
          )}
        </div>
      </div>
      <div className="px-6 py-4">
        {hotspotsData.length === 0 ? (
          <p className="text-gray-500">No hotspots detected</p>
        ) : (
          <div className="space-y-3">
            {hotspotsData.map((hotspot) => (
              <div key={hotspot.latitude + hotspot.longitude} className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
                <div>
                  <h3 className="font-medium text-gray-900">
                    {hotspot.latitude}, {hotspot.longitude}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {hotspot.satellite} ({hotspot.instrument}) |
                    {hotspot.daynight === 'D' ? 'Day' : 'Night'} |
                    {new Date(hotspot.detected_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-1">
                    <svg className="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10.293 3.293l1.414 1.414L16 5.83l-1.414 1.414L10.293 10.293l-1.416 1.414-1.414-1.414L4.17 5.83l1.414-1.414z" />
                    </svg>
                    Confidence: {hotspot.confidence?.toFixed(1)}%
                  </div>
                  {hotspot.frp !== null && (
                    <span className="flex items-center space-x-1 text-sm">
                      <svg className="h-4 w-4 text-orange-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2a4.95 4.95 0 013.47 1.3l1.09 1.09a1 1 0 011.42.58l1.09 1.09a1 1 0 01.58 1.42l1.09 1.09c.39.39.39 1.02 0 1.41l-1.09 1.09a1 1 0 01-.58 1.42l-1.09 1.09a1 1 0 01-1.42.58l-1.09 1.09A4.95 4.95 0 0112 22a4.95 4.95 0 01-3.47-1.3l-1.09-1.09a1 1 0 01-1.42-.58l-1.09-1.09a1 1 0 01-.58-1.42l-1.09-1.09a1 1 0 01-.39-.39l1.09-1.09c.39-.39 1.02-.39 1.41 0l1.09 1.09a1 1 0 011.42.58l1.09 1.09a1 1 0 01.58 1.42l1.09 1.09c.39.39.39 1.02 0 1.41l-1.09 1.09a1 1 0 01-.58 1.42l-1.09 1.09a1 1 0 01-1.42-.58l-1.09-1.09z" />
                      </svg>
                      FRP: {hotspot.frp?.toFixed(2)} MW
                    </span>
                  )}
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      hotspot.severity === 'LOW'
                        ? 'bg-green-100 text-green-800'
                        : hotspot.severity === 'MEDIUM'
                        ? 'bg-yellow-100 text-yellow-800'
                        : hotspot.severity === 'HIGH'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {hotspot.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}