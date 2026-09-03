"use client";

import React from "react";
import { Activity } from "../lib/api";

interface BusinessActionsViewProps {
  activities: Activity[];
}

export const BusinessActionsView: React.FC<BusinessActionsViewProps> = ({ activities }) => {
  const toolActivities = activities.filter(
    (a) => a.source === "business_tool" || a.type === "agent_action"
  );

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 mb-6">
      <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-3 border-b border-slate-800 pb-2">
        <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Simulated Business Tools Executed ({toolActivities.length})
      </h3>

      <div className="space-y-2 text-xs">
        {toolActivities.length === 0 ? (
          <div className="p-4 text-center text-slate-500 italic border border-dashed border-slate-800 rounded-lg">
            No business tool actions executed yet.
          </div>
        ) : (
          toolActivities.map((act) => (
            <div key={act.id} className="bg-slate-800/50 border border-slate-800 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-indigo-300 font-semibold">{act.content}</span>
                <span className="text-[10px] text-slate-500">{new Date(act.created_at).toLocaleTimeString()}</span>
              </div>
              {act.activity_metadata && Object.keys(act.activity_metadata).length > 0 && (
                <pre className="text-[10px] font-mono text-slate-400 bg-slate-950/60 p-2 rounded mt-1 overflow-x-auto">
                  {JSON.stringify(act.activity_metadata, null, 2)}
                </pre>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
