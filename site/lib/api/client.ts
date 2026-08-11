// Client HTTP centralisé — TOUS les appels au backend passent par ici.
// Ne jamais faire fetch("http://...") ailleurs dans le code.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000/api";

export class ApiError extends Error {
  kind: "network" | "http";
  status?: number;

  constructor(message: string, kind: "network" | "http", status?: number) {
    super(message);
    this.kind = kind;
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError(
      "Le service TrustLine est momentanément indisponible. Réessayez dans quelques instants.",
      "network"
    );
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    const message =
      (detail && typeof detail === "object" && "detail" in detail && String(detail.detail)) ||
      `Le serveur a répondu avec une erreur (${res.status}).`;
    throw new ApiError(message, "http", res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}
