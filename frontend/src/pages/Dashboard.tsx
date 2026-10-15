import { useState } from "react";
import { MapPinned, Route as RouteIcon, Truck } from "lucide-react";
import RoutePlanner from "../components/routing/RoutePlanner";
import RouteResults from "../components/routing/RouteResults";
import RouteMap from "../components/map/RouteMap";
import WeatherHeatmap from "../components/weather/WeatherHeatmap";
import { analyzeRoute } from "../services/route.service";
import { getApiErrorMessage } from "../utils/apiError";
import type { RouteAnalysisRequest, RouteAnalysisResponse } from "../types/routing";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RouteAnalysisResponse | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState<number | null>(null);

  async function handleAnalyze(values: RouteAnalysisRequest) {
    if (loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setSelectedRouteId(null);
    try {
      const response = await analyzeRoute(values);
      setResult(response);
      setSelectedRouteId(response.recommended_route ?? response.routes[0]?.id ?? null);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  const selectedRoute = result?.routes.find((route) => route.id === selectedRouteId);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-5 py-5 md:px-10">
        <div className="mx-auto flex max-w-7xl items-center gap-3">
          <Truck className="text-blue-600" size={30} />
          <div><h1 className="text-xl font-bold">Spotter Weather Routing</h1><p className="text-sm text-slate-500">Weather-aware truck route planning</p></div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl space-y-6 px-5 py-8 md:px-10">
        <div><h2 className="text-2xl font-bold">Route Planner</h2><p className="mt-1 text-slate-600">Compare truck routes and identify weather risks before departure.</p></div>
        <div className="grid items-start gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-2 flex items-center gap-2 text-lg font-semibold"><RouteIcon size={20} className="text-blue-600" /> Plan Your Route</h3>
            <p className="mb-5 text-sm text-slate-500">Enter your trip details to analyze routes.</p>
            <RoutePlanner onAnalyze={handleAnalyze} loading={loading} />
            {error && <p role="alert" className="mt-4 whitespace-pre-line rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          </aside>
          <section className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold"><MapPinned size={20} className="text-blue-600" /> Route Map</h3>
            <RouteMap result={result} selectedRouteId={selectedRouteId} onSelectRoute={setSelectedRouteId} />
          </section>
        </div>
        {result && <RouteResults result={result} selectedRouteId={selectedRouteId} onSelectRoute={setSelectedRouteId} />}
        {result && selectedRoute ? (
          <WeatherHeatmap key={`${result.departure_time}-${result.origin}-${result.destination}-${selectedRoute.id}`} result={result} route={selectedRoute} />
        ) : (
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold">48-Hour Weather Risk Forecast</h3>
            <p className="mt-2 text-sm text-slate-500">Analyze a route to generate its forecast heatmap.</p>
          </section>
        )}
      </main>
    </div>
  );
}
