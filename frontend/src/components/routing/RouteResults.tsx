
import {
  Route as RouteIcon,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

import type {
  AnalyzedRoute,
  RouteAnalysisResponse,
} from "../../types/routing";

interface RouteResultsProps {
  result: RouteAnalysisResponse;
  selectedRouteId: number | null;
  onSelectRoute: (routeId: number) => void;
}

interface RouteCardProps {
  route: AnalyzedRoute;
  selected: boolean;
  recommended: boolean;
  onSelect: () => void;
}

function RouteCard({
  route,
  selected,
  recommended,
  onSelect,
}: RouteCardProps) {
  const risk = route.risk_summary;

  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      className={`w-full rounded-xl border-2 p-5 text-left transition hover:shadow-md ${
        selected
          ? "border-blue-500 bg-blue-50"
          : "border-slate-200 bg-white hover:border-blue-300"
      }`}
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h4 className="text-lg font-bold text-slate-900">
          Route {route.id}
        </h4>

        <div className="flex flex-wrap gap-2">
          {recommended && (
            <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
              <ShieldCheck size={14} />
              Recommended
            </span>
          )}

          {selected && (
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
              Selected
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-slate-500">Distance</p>
          <p className="font-semibold text-slate-900">
            {route.distance_miles.toFixed(2)} mi
          </p>
        </div>

        <div>
          <p className="text-slate-500">Duration</p>
          <p className="font-semibold text-slate-900">
            {route.duration_hours.toFixed(2)} hrs
          </p>
        </div>

        <div>
          <p className="text-slate-500">Average Risk</p>
          <p className="font-semibold text-slate-900">
            {risk.average_risk_score?.toFixed(2) ?? "Unavailable"}
          </p>
        </div>

        <div>
          <p className="text-slate-500">Checkpoints</p>
          <p className="font-semibold text-slate-900">
            {route.checkpoints.length}
          </p>
        </div>
      </div>

      <div className="mt-4 space-y-1 border-t border-slate-200 pt-3 text-sm text-slate-600">
        <p>Severe: {risk.severe_miles.toFixed(1)} mi</p>
        <p>High risk: {risk.high_miles.toFixed(1)} mi</p>
        <p>No travel: {risk.no_travel_miles.toFixed(1)} mi</p>
        <p>Missing forecasts: {risk.unavailable_checkpoints}</p>
      </div>
    </button>
  );
}

export default function RouteResults({
  result,
  selectedRouteId,
  onSelectRoute,
}: RouteResultsProps) {
  const recommendedRoute = result.routes.find(
    (route) => route.id === result.recommended_route
  );

  const hasHighRisk =
    recommendedRoute !== undefined &&
    (recommendedRoute.risk_summary.high_miles > 0 ||
      recommendedRoute.risk_summary.severe_miles > 0);

  const hasModerateRisk =
    recommendedRoute !== undefined &&
    !hasHighRisk &&
    recommendedRoute.risk_summary.average_risk_score !== null &&
    recommendedRoute.risk_summary.average_risk_score > 0;

  return (
    <section
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
      aria-live="polite"
    >
      <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold">
        <RouteIcon size={20} className="text-blue-600" />
        Route Comparison
      </h3>

      {/* No eligible route warning */}
      {result.recommended_route === null && (
        <div
          role="alert"
          className="mb-4 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
        >
          <AlertTriangle
            size={20}
            className="mt-0.5 shrink-0"
          />

          <div>
            <p className="font-semibold">
              No route recommendation available
            </p>

            <p className="mt-1">
              No route currently meets the safety recommendation
              criteria. Routes may contain no-travel conditions
              or missing weather forecasts.
            </p>

            <p className="mt-1">
              You can inspect the alternatives, but none is recommended.
            </p>
          </div>
        </div>
      )}

      {/* High or severe weather warning */}
      {hasHighRisk && recommendedRoute && (
        <div
          role="alert"
          className="mb-4 flex items-start gap-3 rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm text-orange-900"
        >
          <AlertTriangle
            size={20}
            className="mt-0.5 shrink-0 text-orange-600"
          />

          <div>
            <p className="font-semibold">
              Weather risk warning — Route {recommendedRoute.id}
            </p>

            <p className="mt-1">
              Route {recommendedRoute.id} is the lowest-risk eligible
              alternative, but it still contains potentially hazardous
              weather conditions.
            </p>

            <div className="mt-2 space-y-1">
              {recommendedRoute.risk_summary.high_miles > 0 && (
                <p>
                  <strong>
                    {recommendedRoute.risk_summary.high_miles.toFixed(1)} miles
                  </strong>{" "}
                  have HIGH weather risk.
                </p>
              )}

              {recommendedRoute.risk_summary.severe_miles > 0 && (
                <p>
                  <strong>
                    {recommendedRoute.risk_summary.severe_miles.toFixed(1)} miles
                  </strong>{" "}
                  have SEVERE weather risk.
                </p>
              )}
            </div>

            <p className="mt-2 font-medium">
              Recommended does not mean risk-free. Review the
              forecast and road conditions before departure.
            </p>
          </div>
        </div>
      )}

      {/* Moderate weather advisory */}
      {hasModerateRisk && recommendedRoute && (
        <div
          role="status"
          className="mb-4 flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900"
        >
          <ShieldCheck
            size={20}
            className="mt-0.5 shrink-0 text-blue-600"
          />

          <div>
            <p className="font-semibold">
              Weather advisory — Route {recommendedRoute.id}
            </p>

            <p className="mt-1">
              Route {recommendedRoute.id} is the lowest-risk eligible
              alternative. Some weather risk remains along the journey.
            </p>

            <p className="mt-2">
              Average risk score:{" "}
              <strong>
                {recommendedRoute.risk_summary.average_risk_score?.toFixed(2)}
              </strong>
            </p>

            <p className="mt-2">
              Review the weather forecast and road conditions
              before departure.
            </p>
          </div>
        </div>
      )}

      {/* Route comparison cards */}
      {result.routes.length === 0 ? (
        <p className="text-sm text-slate-500">
          No truck routes were returned for this journey.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {result.routes.map((route) => (
            <RouteCard
              key={route.id}
              route={route}
              selected={selectedRouteId === route.id}
              recommended={result.recommended_route === route.id}
              onSelect={() => onSelectRoute(route.id)}
            />
          ))}
        </div>
      )}
    </section>
  );
}
