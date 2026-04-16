"use client";

import { useEffect, useState } from "react";
import { supabase, type SwarmAgent } from "../supabase";

export interface SwarmSnapshot {
  agents: SwarmAgent[];
  loading: boolean;
  error: string | null;
  departmentCounts: Record<string, number>;
  activeCount: number;
}

export function useSwarm(): SwarmSnapshot {
  const [agents, setAgents] = useState<SwarmAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchInitial() {
      const { data, error: fetchError } = await supabase
        .from("agents")
        .select("*")
        .order("department")
        .order("name");

      if (cancelled) return;
      if (fetchError) {
        setError(fetchError.message);
        setLoading(false);
        return;
      }
      setAgents((data ?? []) as SwarmAgent[]);
      setLoading(false);
    }

    fetchInitial();

    const channel = supabase
      .channel("swarm-agents")
      .on("postgres_changes", { event: "*", schema: "public", table: "agents" }, (payload) => {
        if (payload.eventType === "INSERT" && payload.new) {
          setAgents((prev) => [...prev, payload.new as SwarmAgent]);
        } else if (payload.eventType === "UPDATE" && payload.new) {
          setAgents((prev) =>
            prev.map((a) => (a.id === payload.new.id ? (payload.new as SwarmAgent) : a)),
          );
        } else if (payload.eventType === "DELETE" && payload.old) {
          setAgents((prev) => prev.filter((a) => a.id !== payload.old.id));
        }
      })
      .subscribe();

    return () => {
      cancelled = true;
      supabase.removeChannel(channel);
    };
  }, []);

  const departmentCounts: Record<string, number> = {};
  for (const agent of agents) {
    departmentCounts[agent.department] = (departmentCounts[agent.department] ?? 0) + 1;
  }

  const activeCount = agents.filter((a) => a.status === "active").length;

  return { agents, loading, error, departmentCounts, activeCount };
}
