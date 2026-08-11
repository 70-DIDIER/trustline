import { apiGet } from "./client";
import type { HealthResponse } from "./types";

export function health() {
  return apiGet<HealthResponse>("/health/");
}
