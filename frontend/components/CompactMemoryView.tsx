"use client";

import React from "react";

interface CompactMemoryViewProps {
  summary: string;
  updatedAt?: string;
}

export const CompactMemoryView: React.FC<CompactMemoryViewProps> = ({ summary, updatedAt }) => {
  const lines = summary ? summary.split("\n").filter((l) => l.trim()) : [];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 mb-6">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Supervisor Compact Working Memory
        </h3>
        <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded font-mono font-medium">
          Context Window Capped
        </span>
      </div>

      <div className="bg-slate-950 border border-slate-800/80 rounded-lg p-3 text-xs font-mono text-indigo-200 leading-relaxed">
        {lines.length === 0 ? (
          <span className="text-slate-500 italic">[No working memory records initialized]</span>
        ) : (
          lines.map((line, idx) => (
            <div key={idx} className="py-0.5 flex items-start gap-2">
              <span className="text-slate-500 select-none">•</span>
              <span>{line.replace(/^-\s*/, "")}</span>
            </div>
          ))
        )}
      </div>

      {updatedAt && (
        <div className="text-[10px] text-slate-500 mt-2 text-right">
          Last compacted: {new Date(updatedAt).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};
