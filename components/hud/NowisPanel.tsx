"use client";

import "./nowis.css";
import { useSwarm } from "@/lib/hooks/useSwarm";

const NOWIS_URL = process.env.NEXT_PUBLIC_NOWIS_URL ?? "http://localhost:5173";

export default function NowisPanel() {
  const { agents, loading, error, departmentCounts, activeCount } = useSwarm();

  if (error) {
    return (
      <div className="nowis-panel nowis-panel--error">
        <div className="nowis-panel__title">NOWIS Swarm</div>
        <div className="nowis-panel__body">
          connection error: {error}
          <br />
          <small style={{ opacity: 0.6 }}>
            url: {(process.env.NEXT_PUBLIC_SUPABASE_URL ?? "MISSING").slice(0, 25)}...
            {" | "}
            key: {(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "MISSING").slice(0, 10)}...
          </small>
        </div>
      </div>
    );
  }

  return (
    <div className="nowis-panel">
      <div className="nowis-panel__title">NOWIS Swarm</div>
      <div className="nowis-panel__stats">
        <span className="nowis-panel__stat">
          <span className="nowis-panel__stat-num">{loading ? "..." : agents.length}</span>
          <span className="nowis-panel__stat-label">agents</span>
        </span>
        <span className="nowis-panel__stat">
          <span className="nowis-panel__stat-num">
            {loading ? "..." : Object.keys(departmentCounts).length}
          </span>
          <span className="nowis-panel__stat-label">depts</span>
        </span>
        <span className="nowis-panel__stat nowis-panel__stat--live">
          <span className="nowis-panel__stat-num">{loading ? "..." : activeCount}</span>
          <span className="nowis-panel__stat-label">active</span>
        </span>
      </div>
      <a className="nowis-panel__cta" href={NOWIS_URL} target="_blank" rel="noopener noreferrer">
        Enter NOWIS Command Center →
      </a>
    </div>
  );
}
