
import type { LineString } from "geojson";

export type CheckpointInterval = 10 | 25 | 50;

export interface RouteAnalysisRequest {
  origin: string;
  destination: string;
  departure_time: string;
  load_weight: number;
  checkpoint_interval: CheckpointInterval;
}

export interface RouteCheckpoint {
  latitude: number;
  longitude: number;
  mile_marker: number;
  [key: string]: unknown;
}

export interface RouteRiskSummary {
  unavailable_checkpoints: number;
  no_travel_miles: number;
  severe_miles: number;
  high_miles: number;
  average_risk_score: number | null;
}

export interface AnalyzedRoute {
  id: number;
  distance_miles: number;
  duration_hours: number;
  geometry: LineString;
  checkpoints: RouteCheckpoint[];
  risk_summary: RouteRiskSummary;
}

export interface RouteAnalysisResponse {
  origin: string;
  destination: string;
  departure_time: string;
  load_weight: number;
  checkpoint_interval: CheckpointInterval;
  routes: AnalyzedRoute[];
  recommended_route: number | null;
}
