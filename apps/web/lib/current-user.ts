import { cache } from "react";

import { apiGet } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";

export const getCurrentUser = cache(async (): Promise<CurrentUser | null> => {
  try {
    return await apiGet<CurrentUser>("/api/me");
  } catch {
    return null;
  }
});