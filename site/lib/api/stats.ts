import { apiGet } from "./client";
import type { AlertePublique, Stats } from "./types";

export function getStats() {
  return apiGet<Stats>("/stats/");
}

export function getAlertes() {
  return apiGet<AlertePublique[]>("/alertes/");
}
