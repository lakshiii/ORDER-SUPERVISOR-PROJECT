"use client";

import React, { useState } from "react";

interface LiveInstructionsProps {
  onAddInstruction: (instruction: string) => Promise<void>;
  isSubmitting: boolean;
  disabled: boolean;
}

export const LiveInstructions: React.FC<LiveInstructionsProps> = ({
  onAddInstruction,
  isSubmitting,
  disabled,
}) => {
  const [instruction, setInstruction] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instruction.trim()) {
      setErrorMsg("Instruction text cannot be empty.");
      return;
    }
    setErrorMsg("");
    setSuccessMsg("");
    try {
      await onAddInstruction(instruction.trim());
      setSuccessMsg("Live instruction added successfully!");
      setInstruction("");
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to add live instruction.");
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 mb-6">
      <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-3">
        <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        Live Run-Specific Instructions
      </h3>

      {errorMsg && (
        <div className="mb-3 p-2 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs rounded-lg">
          {errorMsg}
        </div>
      )}
      {successMsg && (
        <div className="mb-3 p-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs rounded-lg">
          {successMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3 text-xs">
        <div>
          <label className="block text-slate-300 font-medium mb-1">
            Operator Instruction <span className="text-slate-500 font-normal">(Appended to run instructions)</span>
          </label>
          <textarea
            rows={2}
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            disabled={disabled}
            placeholder="e.g., Prioritize payment issue resolution before replying to customer. Do not contact customer directly."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 text-xs focus:outline-none focus:border-indigo-500 disabled:opacity-50 resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting || disabled}
          className="w-full bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-700 text-slate-200 font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
        >
          {isSubmitting ? "Adding Instruction..." : "Add Live Instruction"}
        </button>
      </form>
    </div>
  );
};
