import { apiPost } from "./client";
import type { Signalement, SignalementInput } from "./types";

export function creerSignalement(input: SignalementInput) {
  return apiPost<Signalement>("/signalements/", input);
}
