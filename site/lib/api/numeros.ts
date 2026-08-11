import { apiGet, apiPost } from "./client";
import type { NumeroDetail, VerdictNumero } from "./types";

export function verifierNumero(numero: string) {
  return apiPost<VerdictNumero>("/numeros/verifier/", { numero });
}

export function getNumero(numero: string) {
  return apiGet<NumeroDetail>(`/numeros/${encodeURIComponent(numero)}/`);
}
