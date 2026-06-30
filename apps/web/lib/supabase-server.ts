import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

import type { Session, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

export async function createClient(): Promise<SupabaseClient> {
  const cookieStore = await cookies();
  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        } catch {
          // setAll is called from a Server Component where cookies can't be
          // mutated. The middleware refreshes the session, so this is safe.
        }
      },
    },
  });
}

export async function getSession(): Promise<Session | null> {
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  return data.session;
}

export async function getAccessToken(): Promise<string | null> {
  const session = await getSession();
  return session?.access_token ?? null;
}