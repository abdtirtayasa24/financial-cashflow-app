import { NextRequest } from "next/server";

import { getAccessToken } from "@/lib/supabase-server";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ id: string; attachmentId: string }> }
) {
  const { id, attachmentId } = await context.params;
  const token = await getAccessToken();

  const upstream = await fetch(
    `${BASE_URL}/api/transactions/${id}/attachments/${attachmentId}/download`,
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      cache: "no-store",
    }
  );

  const headers = new Headers();
  const contentType = upstream.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const disposition = upstream.headers.get("content-disposition");
  if (disposition) headers.set("content-disposition", disposition);

  return new Response(upstream.body, {
    status: upstream.status,
    headers,
  });
}