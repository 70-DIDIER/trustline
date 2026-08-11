import { apiPost } from "./client";
import type { VerdictLien } from "./types";

export function analyserLien(url: string) {
  return apiPost<VerdictLien>("/liens/analyser/", { url });
}
