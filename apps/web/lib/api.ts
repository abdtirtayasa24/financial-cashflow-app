import { getAccessToken } from "@/lib/supabase-server";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const token = await getAccessToken();
  const headers = new Headers(init?.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  return res;
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await apiFetch(path);
  if (!res.ok) {
    throw new Error(`API ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export async function apiSend<T>(
  path: string,
  method: string,
  body?: unknown
): Promise<T> {
  const res = await apiFetch(path, {
    method,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(detail || `API ${res.status}`);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}