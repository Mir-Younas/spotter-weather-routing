import axios from "axios";

function readable(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(readable).join(", ");
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, entry]) => `${key}: ${readable(entry)}`)
      .join("\n");
  }
  return String(value ?? "Unknown error");
}

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : "An unexpected error occurred.";
  }
  if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
    return "The request timed out. Please try again.";
  }
  if (!error.response) {
    return "Cannot reach Django. Check that the backend is running and CORS is configured.";
  }
  const { status, data } = error.response;
  if (status >= 500) return "The server encountered an error. Please try again later.";
  if (data !== undefined && data !== null && data !== "") {
    return readable(data);
  }
  return `Request failed (${status}).`;
}
