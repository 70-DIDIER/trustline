import { apiPost } from "./client";
import type { VerdictMessage } from "./types";

export function analyserMessage(contenu: string) {
  return apiPost<VerdictMessage>("/messages/analyser/", { contenu });
}
