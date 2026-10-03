interface StatsCardsProps {
  totalRegions: number;
  lowRisk: number;
  mediumRisk: number;
  highRisk: number;
  criticalRisk: number;
  activeHotspots: number;
  activeAlerts: number;
}

export default function StatsCards({
  totalRegions,
  lowRisk,
  mediumRisk,
  highRisk,
  criticalRisk,
  activeHotspots,
  activeAlerts
}: StatsCardsProps) {
  return (
    <div className="grid gap-4 mb-6">
      <div className="grid-cols-2 sm:grid-cols-3 lg:grid-cols-7">
        {/* Total Regions */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Monitored Regions</h3>
          <p className="text-2xl font-bold text-gray-900 mt-2">{totalRegions}</p>
        </div>

        {/* Low Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500">Low Risk</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">{lowRisk}</p>
        </div>

        {/* Medium Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <h3 className="text-sm font-medium text-gray-500">Medium Risk</h3>
          <p className="text-2xl font-bold text-yellow-600 mt-2">{mediumRisk}</p>
        </div>

        {/* High Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
          <h3 className="text-sm font-medium text-gray-500">High Risk</h3>
          <p className="text-2xl font-bold text-orange-600 mt-2">{highRisk}</p>
        </div>

        {/* Critical Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
          <h3 className="text-sm font-medium text-gray-500">Critical Risk</h3>
          <p className="text-2xl font-bold text-red-600 mt-2">{criticalRisk}</p>
        </div>

        {/* Active Hotspots */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500">Active Hotspots</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">{activeHotspots}</p>
        </div>

        {/* Active Alerts */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <h3 className="text-sm font-medium text-gray-500">Active Alerts</h3>
          <p className="text-2xl font-bold text-purple-600 mt-2">{activeAlerts}</p>
        </div>
      </div>
    </div>
  );
}