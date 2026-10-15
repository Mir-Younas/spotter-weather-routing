import axiosInstance from "../api/axiosInstance";

import type {
  RouteAnalysisRequest,
  RouteAnalysisResponse,
} from "../types/routing";

import type {
  HeatmapRequest,
  HeatmapResponse,
} from "../types/heatmap";

export const analyzeRoute = async (
  payload: RouteAnalysisRequest
): Promise<RouteAnalysisResponse> => {
  const { data } = await axiosInstance.post<RouteAnalysisResponse>(
    "/routes/analyze/",
    payload
  );

  return data;
};

export const getRouteHeatmap = async (
  payload: HeatmapRequest
): Promise<HeatmapResponse> => {
  const { data } = await axiosInstance.post<HeatmapResponse>(
    "/routes/heatmap/",
    payload
  );

  return data;
};