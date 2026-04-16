"use client";

import { useEffect, useRef } from "react";
import { useStudio } from "@/lib/store";
import { useSwarm } from "@/lib/hooks/useSwarm";

function shortLabel(name: string): string {
  const words = name.split(/\s+/);
  let pick = words[0];
  if (pick.length <= 3 && words.length > 1) {
    pick = words[words.length - 1];
  }
  return pick.length > 8 ? pick.slice(0, 7) + "." : pick;
}

export default function SwarmBridge() {
  const { state, updateSeatConfig } = useStudio();
  const { agents, loading } = useSwarm();
  const appliedRef = useRef(false);

  useEffect(() => {
    if (loading || agents.length === 0 || state.seats.length === 0 || appliedRef.current) return;

    const uniqueDepts = [...new Set(agents.map((a) => a.department))];
    const representatives = uniqueDepts
      .map((dept) => agents.find((a) => a.department === dept))
      .filter(Boolean);
    const pool = representatives.length >= state.seats.length ? representatives : agents;

    state.seats.forEach((seat, i) => {
      const agent = pool[i % pool.length];
      if (!agent) return;
      updateSeatConfig(seat.seatId, {
        label: shortLabel(agent.name),
        roleTitle: agent.department,
      });
    });

    appliedRef.current = true;
  }, [loading, agents, state.seats, updateSeatConfig]);

  return null;
}
