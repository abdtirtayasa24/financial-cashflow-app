const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type Json = unknown;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type") && init?.body) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    throw new Error(`API request failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export const apiClient = {
  get: <T extends Json>(path: string) => request<T>(path),
  post: <T extends Json>(path: string, body: Json) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};