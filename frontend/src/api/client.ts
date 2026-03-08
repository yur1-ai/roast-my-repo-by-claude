import type {
  RoastFeedResponse,
  RoastResponse,
  RoastSubmitResponse,
} from "@/types/roast";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

export async function submitRoast(
  repoUrl: string,
  brutalityLevel: number
): Promise<RoastSubmitResponse> {
  return request<RoastSubmitResponse>("/api/roast", {
    method: "POST",
    body: JSON.stringify({ repo_url: repoUrl, brutality_level: brutalityLevel }),
  });
}

export async function getRoast(id: string): Promise<RoastResponse> {
  return request<RoastResponse>(`/api/roast/${id}`);
}

export async function getRecentRoasts(
  limit = 20,
  offset = 0
): Promise<RoastFeedResponse> {
  return request<RoastFeedResponse>(
    `/api/roasts/recent?limit=${limit}&offset=${offset}`
  );
}
