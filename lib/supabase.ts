import { createClient } from "@supabase/supabase-js";

// Build-time inlined by Next.js. If Turbopack caches this module, env changes
// require a source-level edit to bust the cache and trigger recompilation.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local",
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface SwarmAgent {
  id: string;
  name: string;
  slug: string;
  department: string;
  role: string | null;
  philosophy: string | null;
  collaborates_with: string[];
  status: string;
  last_active: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SwarmActivity {
  id: string;
  agent_id: string;
  event_type: string;
  context: string | null;
  session_id: string | null;
  created_at: string;
}

export type DerivedStatus = "active" | "idle" | "dormant";

export function computeDerivedStatus(lastActive: string | null): DerivedStatus {
  if (!lastActive) return "dormant";
  const diffHours = (Date.now() - new Date(lastActive).getTime()) / (1000 * 60 * 60);
  if (diffHours < 24) return "active";
  if (diffHours < 24 * 7) return "idle";
  return "dormant";
}
