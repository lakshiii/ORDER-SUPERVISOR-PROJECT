"use client";

import React from "react";
import { Activity } from "../lib/api";

interface TimelineViewProps {
  activities: Activity[];
}

export const TimelineView: React.FC<TimelineViewProps> = ({ activities }) => {
  const sorted = [...activities].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const getSourceBadge = (source: string, type: string) => {
    if (source === "user_control" || type === "manual_instruction") {
      return <span className="bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">USER CONTROL</span>;
    }
    if (source === "ai_supervisor_agent" || type === "agent_action") {
      return <span className="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">AI AGENT</span>;
    }
    if (source === "business_tool") {
      return <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">BUSINESS TOOL</span>;
    }
    if (source === "wake_sleep_policy") {
      return <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] px-2 py-0.5 rounded font-mono font-medium">POLICY</span>;
    }
    return <span className="bg-slate-800 text-slate-400 border border-slate-700 text-[10px] px-2 py-0.5 rounded font-mono">{source.toUpperCase()}</span>;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 mb-6">
      <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-3 border-b border-slate-800 pb-2">
        <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Chronological Activities & Signals Timeline ({activities.length})
      </h3>

      <div className="space-y-2 text-xs max-h-[420px] overflow-y-auto pr-1">
        {sorted.length === 0 ? (
          <div className="p-4 text-center text-slate-500 italic border border-dashed border-slate-800 rounded-lg">
            No timeline activities logged for this run yet.
          </div>
        ) : (
          sorted.map((act) => (
            <div key={act.id} className="bg-slate-800/40 border border-slate-800/80 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  {getSourceBadge(act.source, act.type)}
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">{act.type}</span>
                </div>
                <span className="text-[10px] text-slate-500">{new Date(act.created_at).toLocaleTimeString()}</span>
              </div>
              <p className="text-slate-200 text-xs font-medium mt-1">{act.content}</p>

              {act.activity_metadata && Object.keys(act.activity_metadata).length > 0 && (
                <details className="mt-1">
                  <summary className="text-[10px] text-indigo-400 cursor-pointer hover:underline font-mono">
                    View Activity Metadata
                  </summary>
                  <pre className="text-[10px] font-mono text-slate-400 bg-slate-950/80 p-2 rounded mt-1 overflow-x-auto">
                    {JSON.stringify(act.activity_metadata, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
