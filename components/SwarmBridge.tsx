"use client";

import { useEffect, useRef } from "react";
import { useStudio } from "@/lib/store";
import { useSwarm } from "@/lib/hooks/useSwarm";

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
        label: agent.name,
        roleTitle: agent.department,
      });
    });

    appliedRef.current = true;
  }, [loading, agents, state.seats, updateSeatConfig]);

  return null;
}
