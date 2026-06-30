import type { Session } from "@supabase/supabase-js";
import { supabaseBrowser } from "./supabase-browser";

export async function getSession(): Promise<Session | null> {
  const { data } = await supabaseBrowser.auth.getSession();
  return data.session;
}