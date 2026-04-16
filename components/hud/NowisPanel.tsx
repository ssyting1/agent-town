"use client";

import "./nowis.css";
import { useState } from "react";
import { useSwarm } from "@/lib/hooks/useSwarm";

const NOWIS_URL = process.env.NEXT_PUBLIC_NOWIS_URL ?? "http://localhost:5173";

function shortLabel(name: string): string {
  const words = name.split(/\s+/);
  let pick = words[0];
  if (pick.length <= 3 && words.length > 1) {
    pick = words[words.length - 1];
  }
  return pick.length > 8 ? pick.slice(0, 7) + "." : pick;
}

export default function NowisPanel() {
  const { agents, loading, error, departmentCounts, activeCount } = useSwarm();
  const [expanded, setExpanded] = useState(false);

  if (error) {
    return (
      <div className="nowis-panel nowis-panel--error">
        <div className="nowis-panel__title">NOWIS Swarm</div>
        <div className="nowis-panel__body">connection error: {error}</div>
      </div>
    );
  }

  const deptEntries = Object.entries(departmentCounts).sort(([, a], [, b]) => b - a);

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
      {!loading && agents.length > 0 && (
        <button
          type="button"
          className="nowis-panel__toggle"
          onClick={() => setExpanded((prev) => !prev)}
        >
          {expanded ? "Hide roster ▲" : "Show roster ▼"}
        </button>
      )}
      {expanded && (
        <div className="nowis-panel__roster">
          {deptEntries.map(([dept, count]) => (
            <div key={dept} className="nowis-panel__dept">
              <div className="nowis-panel__dept-name">
                {dept} <span className="nowis-panel__dept-count">{count}</span>
              </div>
              <div className="nowis-panel__dept-agents">
                {agents
                  .filter((a) => a.department === dept)
                  .map((a) => (
                    <span key={a.id} className="nowis-panel__agent-pill">
                      {shortLabel(a.name)}
                    </span>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}
      <a className="nowis-panel__cta" href={NOWIS_URL} target="_blank" rel="noopener noreferrer">
        Enter NOWIS Command Center →
      </a>
    </div>
  );
}
