import { useState } from "react";
import { CloudSun, LoaderCircle } from "lucide-react";
import { getRouteHeatmap } from "../../services/route.service";
import { getApiErrorMessage } from "../../utils/apiError";
import type { AnalyzedRoute, RouteAnalysisResponse } from "../../types/routing";
import type { HeatmapCheckpoint, HeatmapHour, HeatmapResponse } from "../../types/heatmap";

interface Props {
  result: RouteAnalysisResponse;
  route: AnalyzedRoute;
}

function validCheckpoints(route: AnalyzedRoute): HeatmapCheckpoint[] {
  return route.checkpoints.flatMap((checkpoint) => {
    const latitude = checkpoint.latitude;
    const longitude = checkpoint.longitude;
    const mileMarker = checkpoint.mile_marker;
    if (
      typeof latitude !== "number" || !Number.isFinite(latitude) || latitude < -90 || latitude > 90 ||
      typeof longitude !== "number" || !Number.isFinite(longitude) || longitude < -180 || longitude > 180 ||
      typeof mileMarker !== "number" || !Number.isFinite(mileMarker) || mileMarker < 0
    ) return [];
    return [{ latitude, longitude, mile_marker: mileMarker }];
  });
}

function riskColor(level: string): string {
  switch (level.toUpperCase()) {
    case "LOW": case "SAFE": return "bg-emerald-400";
    case "MODERATE": case "MEDIUM": return "bg-amber-300";
    case "HIGH": return "bg-orange-500";
    case "SEVERE": return "bg-red-600";
    case "NO_TRAVEL": return "bg-purple-800";
    default: return "bg-slate-300";
  }
}

// The backend estimates checkpoint arrival by proportional route progress.
// Match the closest hourly heatmap column; keep the precise ETA for display.
function estimatedArrivalHour(route: AnalyzedRoute, mileMarker: number): number {
  if (route.distance_miles <= 0 || !Number.isFinite(route.duration_hours)) return 0;
  const elapsed = (mileMarker / route.distance_miles) * route.duration_hours;
  return Math.max(0, Math.min(48, Math.round(elapsed)));
}

function estimatedArrivalOffset(route: AnalyzedRoute, mileMarker: number): number {
  if (route.distance_miles <= 0 || !Number.isFinite(route.duration_hours)) return 0;
  return (mileMarker / route.distance_miles) * route.duration_hours;
}

function fmt(value: number | null | undefined, unit: string): string {
  return typeof value === "number" ? `${value.toFixed(1)} ${unit}` : "Unavailable";
}

export default function WeatherHeatmap({ result, route }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [heatmap, setHeatmap] = useState<HeatmapResponse | null>(null);
  const [hour, setHour] = useState(0);
  const [locationIndex, setLocationIndex] = useState(0);
  const checkpoints = validCheckpoints(route);

  async function loadHeatmap() {
    if (loading) return;
    setLoading(true);
    setError(null);
    setHeatmap(null);
    try {
      if (checkpoints.length !== route.checkpoints.length) {
        throw new Error("Some route checkpoints are missing valid latitude, longitude, or mile marker values.");
      }
      if (checkpoints.length === 0 || checkpoints.length > 200) {
        throw new Error("The heatmap requires between 1 and 200 route checkpoints.");
      }
      const data = await getRouteHeatmap({
        checkpoints,
        departure_time: result.departure_time,
        load_weight: result.load_weight,
      });
      setHeatmap(data);
      setHour(0);
      setLocationIndex(0);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  const selectedLocation = heatmap?.locations[locationIndex];
  const selectedForecast: HeatmapHour | undefined = selectedLocation?.hours.find((item) => item.offset_hours === hour);
  const arrivalOffset = selectedLocation ? estimatedArrivalOffset(route, selectedLocation.mile_marker) : null;
  const arrivalHour = selectedLocation ? estimatedArrivalHour(route, selectedLocation.mile_marker) : null;
  const arrivalForecast = selectedLocation?.hours.find((item) => item.offset_hours === arrivalHour);
  const estimatedArrivalTime = arrivalOffset !== null
    ? new Date(new Date(result.departure_time).getTime() + arrivalOffset * 3600000)
    : null;
  const forecastTime = heatmap ? new Date(new Date(heatmap.start_time).getTime() + hour * 3600000) : null;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="flex items-center gap-2 text-lg font-semibold"><CloudSun size={20} className="text-blue-600" /> 48-Hour Weather Risk Forecast</h3>
          <p className="mt-1 text-sm text-slate-600">Route {route.id} · {checkpoints.length} checkpoints · Forecast risk by mile marker and hour</p>
        </div>
        <button type="button" disabled={loading} onClick={loadHeatmap}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
          {loading && <LoaderCircle size={16} className="animate-spin" />}
          {loading ? "Loading forecast..." : heatmap ? "Refresh forecast" : "Generate heatmap"}
        </button>
      </div>

      {error && <p role="alert" className="mt-4 whitespace-pre-line rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {!heatmap && !error && <p className="mt-4 text-sm text-slate-500">Generate a forecast for the selected route. The API samples up to 20 locations across the route.</p>}

      {heatmap && (
        <div className="mt-5 space-y-4">
          <div className="rounded-xl bg-slate-50 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
              <label htmlFor="forecast-hour" className="font-semibold">Forecast hour: +{hour}h</label>
              <span className="text-slate-600">{forecastTime?.toLocaleString() ?? ""}</span>
            </div>
            <input id="forecast-hour" aria-label="Forecast hour" type="range" min={0} max={48} step={1} value={hour}
              onChange={(event) => setHour(Number(event.target.value))} className="mt-3 w-full accent-blue-600" />
            <div className="flex justify-between text-xs text-slate-500"><span>Departure</span><span>+24h</span><span>+48h</span></div>
          </div>

          <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-600">
            {[["LOW", "Low"], ["MODERATE", "Moderate"], ["HIGH", "High"], ["SEVERE", "Severe"], ["NO_TRAVEL", "No travel"], ["UNKNOWN", "Unknown"]].map(([level, label]) => (
              <span key={level} className="flex items-center gap-1"><span className={`inline-block h-3 w-3 rounded-sm ${riskColor(level)}`} />{label}</span>
            ))}
          </div>

          <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
            <p className="font-semibold">Estimated truck arrival overlay</p>
            <p className="mt-1">Each row has a blue ring around the forecast hour closest to the truck’s estimated arrival. This is based on route distance and estimated driving duration; it does not account for stops or changing traffic.</p>
            <p className="mt-1">The recommended route is chosen using weather at estimated checkpoint arrival times, prioritizing fewer severe and high-risk miles, then average risk and duration. A future hazard outside the travel window does not automatically disqualify a route.</p>
          </div>
          <p className="text-xs text-slate-500">Rows represent sampled route locations; columns represent forecast hours. Select a cell to inspect its conditions. Blue ring = estimated truck arrival; dark outline = selected cell.</p>
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full border-collapse text-xs">
              <thead><tr><th className="sticky left-0 z-10 min-w-24 bg-white p-2 text-left">Mile</th>{heatmap.slider_hours.map((h) => (
                <th key={h} className={`min-w-5 px-0.5 py-2 text-center ${h === hour ? "bg-blue-100" : ""}`}>{h % 6 === 0 ? h : ""}</th>
              ))}</tr></thead>
              <tbody>{heatmap.locations.map((location, index) => (
                <tr key={`${index}-${location.mile_marker}`}>
                  <th className="sticky left-0 z-10 bg-white p-2 text-left font-medium">{location.mile_marker.toFixed(1)}</th>
                  {heatmap.slider_hours.map((h) => {
                    const forecast = location.hours.find((item) => item.offset_hours === h);
                    const active = locationIndex === index && hour === h;
                    const atArrival = estimatedArrivalHour(route, location.mile_marker) === h;
                    return <td key={h} className="p-0.5">
                      <button type="button" title={`Mile ${location.mile_marker.toFixed(1)}, +${h}h: ${forecast?.risk_level ?? "UNKNOWN"}${atArrival ? " — estimated truck arrival" : ""}`}
                        aria-label={`Mile ${location.mile_marker.toFixed(1)}, hour ${h}, risk ${forecast?.risk_level ?? "UNKNOWN"}`}
                        aria-pressed={active}
                        onClick={() => { setLocationIndex(index); setHour(h); }}
                        className={`h-6 w-5 rounded-sm ${riskColor(forecast?.risk_level ?? "UNKNOWN")} ${atArrival ? "ring-2 ring-inset ring-blue-700" : ""} ${active ? "outline outline-2 outline-offset-1 outline-slate-950" : ""}`} />
                    </td>;
                  })}</tr>
              ))}</tbody>
            </table>
          </div>

          {selectedLocation && (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm">
              <h4 className="font-semibold">Mile {selectedLocation.mile_marker.toFixed(1)} · Hour +{hour}</h4>
              <p className="mt-1 text-slate-600">Estimated truck arrival: {estimatedArrivalTime?.toLocaleString() ?? "Unavailable"} (+{arrivalOffset?.toFixed(2) ?? "0.00"}h). Nearest forecast column: +{arrivalHour ?? 0}h.</p>
              <p className="mt-1 text-slate-600">Risk at estimated arrival: <strong>{arrivalForecast?.risk_level ?? "UNKNOWN"}</strong> · Score: {arrivalForecast?.risk_score?.toFixed(2) ?? "Unavailable"}</p>
              <p className="mt-1 text-slate-600">Selected cell risk: <strong>{selectedForecast?.risk_level ?? "UNKNOWN"}</strong> · Score: {selectedForecast?.risk_score?.toFixed(2) ?? "Unavailable"}</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                <span>Temperature: {fmt(selectedForecast?.temperature_f, "°F")}</span>
                <span>Wind: {fmt(selectedForecast?.wind_speed_mph, "mph")}</span>
                <span>Gusts: {fmt(selectedForecast?.wind_gusts_mph, "mph")}</span>
                <span>Precipitation: {fmt(selectedForecast?.precipitation_mm, "mm")}</span>
                <span>Snowfall: {fmt(selectedForecast?.snowfall_cm, "cm")}</span>
                <span>Weather code: {selectedForecast?.weather_code ?? "Unavailable"}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
