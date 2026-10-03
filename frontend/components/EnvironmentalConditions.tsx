import { RiskData } from '@/lib/api';

interface EnvironmentalConditionsProps {
  riskData: RiskData | undefined;
}

export default function EnvironmentalConditions({ riskData }: EnvironmentalConditionsProps) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">
          Environmental Conditions
        </h2>
      </div>
      <div className="px-6 py-4">
        {!riskData ? (
          <p className="text-gray-500">No data available</p>
        ) : (
          <div className="grid gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Temperature</h3>
              <p className="text-2xl font-bold text-gray-900">
                {riskData.temperature}°F
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Humidity</h3>
              <p className="text-2xl font-bold text-gray-900">
                {riskData.humidity}%
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Wind Speed</h3>
              <p className="text-2xl font-bold text-gray-900">
                {riskData.wind_speed} mph
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Rainfall</h3>
              <p className="text-2xl font-bold text-gray-900">
                {riskData.rainfall} in
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}