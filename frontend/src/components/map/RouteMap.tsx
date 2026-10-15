
import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  useMap,
} from "react-leaflet";
import L from "leaflet";

import type { Feature, LineString } from "geojson";
import type {
  AnalyzedRoute,
  RouteAnalysisResponse,
} from "../../types/routing";

import "leaflet/dist/leaflet.css";

interface RouteMapProps {
  result: RouteAnalysisResponse | null;
  selectedRouteId: number | null;
  onSelectRoute: (routeId: number) => void;
}

interface FitRoutesProps {
  routes: AnalyzedRoute[];
}

function FitRoutes({ routes }: FitRoutesProps) {
  const map = useMap();

  useEffect(() => {
    if (routes.length === 0) return;

    const bounds = L.latLngBounds([]);

    for (const route of routes) {
      for (const coordinate of route.geometry.coordinates) {
        bounds.extend([coordinate[1], coordinate[0]]);
      }
    }

    if (bounds.isValid()) {
      map.fitBounds(bounds, {
        padding: [35, 35],
        maxZoom: 12,
      });
    }
  }, [map, routes]);

  return null;
}

function getRouteColor(
  routeId: number,
  selectedRouteId: number | null,
  recommendedRouteId: number | null
): string {
  if (routeId === selectedRouteId) return "#2563eb";
  if (routeId === recommendedRouteId) return "#16a34a";
  return "#94a3b8";
}

export default function RouteMap({
  result,
  selectedRouteId,
  onSelectRoute,
}: RouteMapProps) {
  const routes = result?.routes ?? [];

  return (
    <div className="space-y-3">
      <div className="h-[440px] overflow-hidden rounded-xl border border-slate-200">
        <MapContainer
          center={[39.5, -98.35]}
          zoom={4}
          scrollWheelZoom
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {routes.map((route) => {
            const feature: Feature<LineString> = {
              type: "Feature",
              properties: {},
              geometry: route.geometry,
            };

            const selected = route.id === selectedRouteId;

            return (
              <GeoJSON
                key={`${result?.departure_time}-${route.id}-${selectedRouteId}`}
                data={feature}
                style={{
                  color: getRouteColor(
                    route.id,
                    selectedRouteId,
                    result?.recommended_route ?? null
                  ),
                  weight: selected ? 7 : 4,
                  opacity: selected ? 1 : 0.75,
                }}
                eventHandlers={{
                  click: () => onSelectRoute(route.id),
                }}
              />
            );
          })}

          <FitRoutes routes={routes} />
        </MapContainer>
      </div>

      <div className="flex flex-wrap gap-4 text-xs text-slate-600">
        <span className="flex items-center gap-2">
          <span className="h-1 w-6 rounded bg-blue-600" />
          Selected
        </span>

        <span className="flex items-center gap-2">
          <span className="h-1 w-6 rounded bg-green-600" />
          Recommended
        </span>

        <span className="flex items-center gap-2">
          <span className="h-1 w-6 rounded bg-slate-400" />
          Alternative
        </span>
      </div>

      {routes.length === 0 && (
        <p className="text-sm text-slate-500">
          Analyze a route to display truck routing alternatives.
        </p>
      )}
    </div>
  );
}
