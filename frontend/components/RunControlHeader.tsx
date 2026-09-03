"use client";

import React, { useState } from "react";
import { RunDetail } from "../lib/api";

interface RunControlHeaderProps {
  run: RunDetail;
  onInterrupt: () => Promise<void>;
  onResume: () => Promise<void>;
  onTerminate: () => Promise<void>;
  isActionLoading: boolean;
}

export const RunControlHeader: React.FC<RunControlHeaderProps> = ({
  run,
  onInterrupt,
  onResume,
  onTerminate,
  isActionLoading,
}) => {
  const [showTerminateConfirm, setShowTerminateConfirm] = useState(false);

  const statusLower = run.status.toLowerCase();
  const isInterrupted = statusLower === "interrupted" || statusLower === "paused";
  const isTerminal = statusLower === "completed" || statusLower === "terminated";

  const getStatusBadge = () => {
    switch (statusLower) {
      case "active":
      case "pending":
        return <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs px-2.5 py-1 rounded font-mono font-bold">ACTIVE</span>;
      case "sleeping":
        return <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs px-2.5 py-1 rounded font-mono font-bold">SLEEPING</span>;
      case "interrupted":
      case "paused":
        return <span className="bg-orange-500/20 text-orange-300 border border-orange-500/30 text-xs px-2.5 py-1 rounded font-bold font-mono">PAUSED / INTERRUPTED</span>;
      case "completed":
        return <span className="bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs px-2.5 py-1 rounded font-bold font-mono">COMPLETED</span>;
      case "terminated":
        return <span className="bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs px-2.5 py-1 rounded font-bold font-mono">TERMINATED</span>;
      default:
        return <span className="bg-slate-700 text-slate-200 text-xs px-2.5 py-1 rounded font-bold font-mono">{run.status.toUpperCase()}</span>;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 mb-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-bold text-white">Run #{run.id} Details</h2>
            {getStatusBadge()}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Order ID: <strong className="text-slate-200">{run.order?.external_order_id || run.order_id}</strong> • Workflow:{" "}
            <code className="font-mono text-indigo-300">{run.temporal_workflow_id || `order-supervisor-${run.order_id}`}</code>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {isInterrupted ? (
            <button
              onClick={onResume}
              disabled={isActionLoading}
              className="bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Resume Supervisor
            </button>
          ) : (
            <button
              onClick={onInterrupt}
              disabled={isActionLoading || isTerminal}
              className="bg-amber-600 hover:bg-amber-500 active:bg-amber-700 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Pause / Interrupt
            </button>
          )}

          {!showTerminateConfirm ? (
            <button
              onClick={() => setShowTerminateConfirm(true)}
              disabled={isActionLoading || isTerminal}
              className="bg-rose-700/80 hover:bg-rose-600 active:bg-rose-800 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              Terminate Run
            </button>
          ) : (
            <div className="flex items-center gap-1.5 bg-rose-950/80 border border-rose-800 p-1 rounded-lg">
              <span className="text-[11px] text-rose-300 font-medium px-2">Confirm?</span>
              <button
                onClick={async () => {
                  await onTerminate();
                  setShowTerminateConfirm(false);
                }}
                disabled={isActionLoading}
                className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold px-2.5 py-1 rounded transition-colors"
              >
                Yes, Terminate
              </button>
              <button
                onClick={() => setShowTerminateConfirm(false)}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Grid Meta Information */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider font-semibold">Workflow Status</span>
          <span className="text-slate-200 font-medium">{run.current_status || "Initializing"}</span>
        </div>
        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider font-semibold">Order Status</span>
          <span className="text-indigo-300 font-medium font-mono">{run.order?.status || "created"}</span>
        </div>
        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider font-semibold">Supervisor</span>
          <span className="text-slate-200 font-medium">{run.supervisor?.name || "Order Supervisor"}</span>
        </div>
        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider font-semibold">Last Updated</span>
          <span className="text-slate-200 font-medium">{new Date(run.updated_at).toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
};
