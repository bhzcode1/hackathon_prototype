import { RiskData } from '@/lib/api';

interface RiskOverviewProps {
  riskData: RiskData[];
}

export default function RiskOverview({ riskData }: RiskOverviewProps) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">
          Risk Overview
        </h2>
      </div>
      <div className="px-6 py-4">
        {riskData.length === 0 ? (
          <p className="text-gray-500">No risk data available</p>
        ) : (
          <div className="space-y-3">
            {riskData.map((region) => (
              <div key={region.region} className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
                <div>
                  <h3 className="font-medium text-gray-900">{region.region}</h3>
                  <p className="text-sm text-gray-500">
                    ({region.latitude}, {region.longitude})
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      region.risk_level === 'LOW'
                        ? 'bg-green-100 text-green-800'
                        : region.risk_level === 'MEDIUM'
                        ? 'bg-yellow-100 text-yellow-800'
                        : region.risk_level === 'HIGH'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {region.risk_level}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    {region.risk_score}
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