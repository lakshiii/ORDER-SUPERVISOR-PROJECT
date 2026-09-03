"use client";

import React from "react";

interface HeaderProps {
  isBackendOnline: boolean;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({ isBackendOnline, onRefresh, isRefreshing }) => {
  return (
    <header className="w-full bg-slate-900 text-white border-b border-slate-800 px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold tracking-tight text-white">ORDER SUPERVISOR</h1>
          <span className="text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded font-mono font-medium">
            POC Control Dashboard
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Autonomous AI Order Supervision • Temporal Workflows • Local Llama 3.1:8b
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700 px-3 py-1.5 rounded-lg text-xs">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              isBackendOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
            }`}
          />
          <span className="font-medium text-slate-200">
            Backend API: {isBackendOnline ? "Online (localhost:8000)" : "Disconnected"}
          </span>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-700 text-slate-200 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
        >
          <svg
            className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-indigo-400" : "text-slate-400"}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {isRefreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>
    </header>
  );
};
