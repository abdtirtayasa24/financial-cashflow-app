import { getAccessToken } from "@/lib/supabase-server";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    public readonly detail: string
  ) {
    super(detail || `API ${status} ${statusText}`);
    this.name = "ApiError";
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

async function apiError(res: Response): Promise<ApiError> {
  const detail = await res.text().catch(() => "");
  return new ApiError(res.status, res.statusText, detail);
}

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
    throw await apiError(res);
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
    throw await apiError(res);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  const token = await getAccessToken();
  const headers = new Headers();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  // Intentionally do not set Content-Type so fetch sets the multipart boundary.
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
    cache: "no-store",
  });
  if (!res.ok) {
    throw await apiError(res);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}
