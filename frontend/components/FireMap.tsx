"use client";

import { useEffect, useRef, useState } from "react";
import type { GridRiskData, HotspotData } from "@/lib/api";
import { fetchRiskZones } from "@/lib/api";

function isValidCoord(lat: unknown, lng: unknown): lat is number {
  return (
    typeof lat === "number" &&
    typeof lng === "number" &&
    Number.isFinite(lat) &&
    Number.isFinite(lng) &&
    lat >= -90 &&
    lat <= 90 &&
    lng >= -180 &&
    lng <= 180
  );
}

const FireMap = ({ hotspotsData, center }: { hotspotsData: HotspotData[]; center: [number, number] | null }) => {
  const [riskZones, setRiskZones] = useState<GridRiskData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);

  const mapRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<import("leaflet").Map | null>(null);
  const riskLayerRef = useRef<import("leaflet").LayerGroup | null>(null);
  const hotspotLayerRef = useRef<import("leaflet").LayerGroup | null>(null);
  const leafletRef = useRef<typeof import("leaflet") | null>(null);

  // #region agent log
  const debugLog = (hypothesisId: string, message: string, data: Record<string, unknown>) => {
    fetch("http://127.0.0.1:7654/ingest/e959db23-5300-44a8-9348-974f7876959a", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "27ea16" },
      body: JSON.stringify({
        sessionId: "27ea16",
        runId: "post-fix",
        hypothesisId,
        location: "FireMap.tsx",
        message,
        data,
        timestamp: Date.now(),
      }),
    }).catch(() => {});
  };
  // #endregion

  useEffect(() => {
    let cancelled = false;
    const loadRiskZones = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchRiskZones();
        if (!cancelled) setRiskZones(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) {
          setError("Failed to load risk zones");
          console.error(err);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    loadRiskZones();
    return () => {
      cancelled = true;
    };
  }, []);

  // Create map once when the container mounts (after loading finishes)
  useEffect(() => {
    if (isLoading || error) return;
    if (!mapRef.current) return;

    let cancelled = false;

    import("leaflet").then((L) => {
      if (cancelled || !mapRef.current) return;
      if (mapInstanceRef.current) return;

      leafletRef.current = L;
      const map = L.map(mapRef.current, {
        center: center ?? [20, 0],
        zoom: 2,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      riskLayerRef.current = L.layerGroup().addTo(map);
      hotspotLayerRef.current = L.layerGroup().addTo(map);

      mapInstanceRef.current = map;
      setMapReady(true);
      // #region agent log
      debugLog("L1", "map created", { hasMap: true });
      // #endregion
    });

    return () => {
      cancelled = true;
      setMapReady(false);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
      riskLayerRef.current = null;
      hotspotLayerRef.current = null;
      leafletRef.current = null;
    };
  }, [isLoading, error]);

  // Update layers when data changes — never recreate/remove the map here
  useEffect(() => {
    const map = mapInstanceRef.current;
    const L = leafletRef.current;
    const riskLayer = riskLayerRef.current;
    const hotspotLayer = hotspotLayerRef.current;
    if (!mapReady || !map || !L || !riskLayer || !hotspotLayer) return;

    // #region agent log
    debugLog("L2", "updating layers", {
      riskZones: riskZones.length,
      hotspots: hotspotsData?.length ?? 0,
      mapAlive: !!mapInstanceRef.current,
    });
    // #endregion

    riskLayer.clearLayers();
    for (const zone of riskZones) {
      const { latitude, longitude, risk_score, risk_level, temperature, humidity, wind_speed, rainfall } =
        zone;
      if (!isValidCoord(latitude, longitude)) continue;

      let color = "gray";
      let radius = 5;
      switch (risk_level) {
        case "LOW":
          color = "green";
          radius = 3;
          break;
        case "MEDIUM":
          color = "yellow";
          radius = 5;
          break;
        case "HIGH":
          color = "orange";
          radius = 7;
          break;
        case "CRITICAL":
          color = "red";
          radius = 9;
          break;
      }

      L.circleMarker([latitude, longitude], {
        radius: radius,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.6,
      })
        .bindPopup(
          `<b>Fire Risk Zone</b><br/>ID: ${zone.id}<br/>Risk Score: ${risk_score}<br/>Risk Level: ${risk_level}<br/>Temperature: ${Number(temperature).toFixed(1)}°C<br/>Humidity: ${Number(humidity).toFixed(1)}%<br/>Wind Speed: ${Number(wind_speed).toFixed(1)} km/h<br/>Rainfall: ${Number(rainfall).toFixed(1)} mm<br/><br/>Prediction: FireSight ML<br/>Risk zone generated by FireSight ML model.`
        )
        .addTo(riskLayer);
    }

    // Process hotspots: sort by confidence (desc), FRP (desc), recency (desc) and limit to 25
    let processedHotspots = Array.isArray(hotspotsData) ? hotspotsData : [];
    processedHotspots.sort((a, b) => {
      const confA = a.confidence ?? -Infinity;
      const confB = b.confidence ?? -Infinity;
      if (confB !== confA) return confB - confA;

      const frpA = a.frp ?? -Infinity;
      const frpB = b.frp ?? -Infinity;
      if (frpB !== frpA) return frpB - frpA;

      const dateA = a.detected_at ? new Date(a.detected_at).getTime() : -Infinity;
      const dateB = b.detected_at ? new Date(b.detected_at).getTime() : -Infinity;
      return dateB - dateA;
    });
    processedHotspots = processedHotspots.slice(0, 25);

    hotspotLayer.clearLayers();
    for (const hotspot of processedHotspots) {
      const { latitude, longitude, severity, confidence, frp, satellite, instrument, detected_at, source } =
        hotspot;
      if (!isValidCoord(latitude, longitude)) continue;

      let color = "red";
      switch (severity) {
        case "LOW":
          color = "green";
          break;
        case "MEDIUM":
          color = "yellow";
          break;
        case "HIGH":
          color = "orange";
          break;
      }

      L.circleMarker([latitude, longitude], {
        radius: 7,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      })
        .bindPopup(
          `<b>Fire Detection</b><br/>Source: ${source === "NASA FIRMS" ? "LIVE SATELLITE DATA" : "DEMO DATA"}<br/>Latitude: ${latitude.toFixed(4)}<br/>Longitude: ${longitude.toFixed(4)}<br/>Satellite: ${satellite}<br/>Instrument: ${instrument}<br/>Confidence: ${confidence !== null && confidence !== undefined ? Number(confidence).toFixed(1) + "%" : "N/A"}<br/>FRP: ${frp !== null && frp !== undefined ? Number(frp).toFixed(2) + " MW" : "N/A"}<br/>Severity: ${severity}<br/>Detected at: ${new Date(detected_at).toLocaleString()}`
        )
        .addTo(hotspotLayer);
    }
  }, [mapReady, riskZones, hotspotsData]);

  if (isLoading) {
    return <div className="flex h-96 items-center justify-center">Loading map...</div>;
  }

  if (error) {
    return <div className="flex h-96 items-center justify-center text-red-500">{error}</div>;
  }

  return (
    <>
      <div className="fire-map-container">
        <div ref={mapRef} className="leaflet-map" />
        <div className="map-legend">
          <div className="legend-row">
            <span className="legend-title">FIRE RISK</span>
            <span className="legend-item"><span className="legend-color-low">🟢</span> LOW</span>
            <span className="legend-item"><span className="legend-color-medium">🟡</span> MEDIUM</span>
            <span className="legend-item"><span className="legend-color-high">🟠</span> HIGH</span>
            <span className="legend-item"><span className="legend-color-critical">🔴</span> CRITICAL</span>
          </div>
          <div className="legend-row">
            <span className="legend-title">DATA SOURCES</span>
            <span className="legend-item"><span className="legend-color-firms">🔥</span> NASA FIRMS Hotspot</span>
            <span className="legend-item"><span className="legend-color-risksite">⚪</span> FireSight ML Risk Zone</span>
          </div>
        </div>
      </div>
      <style jsx>{`
        .fire-map-container {
          width: 100%;
        }
        .leaflet-map {
          height: 500px; /* Fixed height for desktop */
          width: 100%;
          background-color: #f0f0f0; /* Placeholder while loading */
        }
        @media (max-width: 640px) {
          .leaflet-map {
            height: 350px; /* Reduced height on mobile */
          }
        }
        .map-legend {
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(4px);
          border-radius: 10px;
          padding: 12px 16px;
          margin-top: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          font-size: 13px;
          line-height: 1.4;
          color: #333;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .legend-row {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          align-items: center;
        }
        .legend-title {
          font-weight: 600;
          min-width: 80px;
        }
        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          white-space: nowrap;
        }
        .legend-color-low {
          color: #22c55e; /* green-600 */
        }
        .legend-color-medium {
          color: #eab308; /* yellow-500 */
        }
        .legend-color-high {
          color: #f97316; /* orange-500 */
        }
        .legend-color-critical {
          color: #ef4444; /* red-500 */
        }
        .legend-color-firms {
          color: #dc2626; /* red-600 */
        }
        .legend-color-risksite {
          color: #6b7280; /* gray-500 */
        }
        @media (max-width: 640px) {
          .map-legend {
            padding: 10px 14px;
            margin-top: 8px;
            font-size: 12px;
          }
          .legend-title {
            min-width: 60px;
            font-size: 12px;
          }
          .legend-item {
            gap: 4px;
          }
        }
      `}</style>
    </>
  );
};

export default FireMap;