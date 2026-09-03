"use client";

import React, { useState } from "react";
import { RunSummary } from "../lib/api";

interface RunListProps {
  runs: RunSummary[];
  selectedRunId: number | null;
  onSelectRun: (runId: number) => void;
}

export const RunList: React.FC<RunListProps> = ({ runs, selectedRunId, onSelectRun }) => {
  const [filter, setFilter] = useState<"all" | "active" | "interrupted" | "completed" | "terminated">("all");

  const filteredRuns = runs.filter((r) => {
    if (filter === "all") return true;
    if (filter === "active") return r.status === "active" || r.status === "pending" || r.status === "sleeping";
    return r.status === filter;
  });

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
      case "pending":
        return <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">ACTIVE</span>;
      case "sleeping":
        return <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">SLEEPING</span>;
      case "interrupted":
      case "paused":
        return <span className="bg-orange-500/20 text-orange-300 border border-orange-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">PAUSED</span>;
      case "completed":
        return <span className="bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">COMPLETED</span>;
      case "terminated":
        return <span className="bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">TERMINATED</span>;
      default:
        return <span className="bg-slate-700 text-slate-300 text-[10px] px-2 py-0.5 rounded font-mono">{status.toUpperCase()}</span>;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          Supervision Runs ({runs.length})
        </h2>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-lg text-xs mb-3 font-medium">
        {(["all", "active", "interrupted", "completed", "terminated"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`flex-1 py-1 rounded text-center capitalize transition-colors ${
              filter === tab
                ? "bg-slate-700 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Run Cards Scrollable */}
      <div className="space-y-2 overflow-y-auto max-h-[380px] pr-1 flex-1">
        {filteredRuns.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg">
            No runs found for filter &apos;{filter}&apos;.
          </div>
        ) : (
          filteredRuns.map((r) => {
            const isSelected = r.id === selectedRunId;
            return (
              <div
                key={r.id}
                onClick={() => onSelectRun(r.id)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? "bg-indigo-950/40 border-indigo-500/50 shadow-sm"
                    : "bg-slate-800/50 border-slate-800 hover:border-slate-700 hover:bg-slate-800"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-xs text-slate-200">
                    Run #{r.id} <span className="text-slate-400 font-normal">(Order #{r.order_id})</span>
                  </span>
                  {getStatusBadge(r.status)}
                </div>
                <div className="text-[11px] text-slate-400 truncate">
                  {r.current_status || "Initializing"}
                </div>
                <div className="text-[10px] text-slate-500 mt-1 flex items-center justify-between">
                  <span>Created: {new Date(r.created_at).toLocaleTimeString()}</span>
                  {r.temporal_workflow_id && (
                    <span className="font-mono text-[9px] text-slate-400">{r.temporal_workflow_id}</span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
