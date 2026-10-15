export interface HeatmapCheckpoint {
  latitude: number;
  longitude: number;
  mile_marker: number;
}

export interface HeatmapRequest {
  checkpoints: HeatmapCheckpoint[];
  departure_time: string;
  load_weight: number;
}

export interface HeatmapHour {
  offset_hours: number;
  forecast_time?: string;
  risk_level: string;
  risk_score: number | null;
  temperature_f?: number | null;
  wind_speed_mph?: number | null;
  wind_gusts_mph?: number | null;
  precipitation_mm?: number | null;
  snowfall_cm?: number | null;
  weather_code?: number | null;
}

export interface HeatmapLocation extends HeatmapCheckpoint {
  hours: HeatmapHour[];
}

export interface HeatmapResponse {
  start_time: string;
  end_time: string;
  slider_hours: number[];
  locations: HeatmapLocation[];
}
