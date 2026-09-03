"use client";

import React, { useState } from "react";
import { SupervisorTemplate } from "../lib/api";

interface StartRunFormProps {
  supervisors: SupervisorTemplate[];
  onStartRun: (data: {
    external_order_id: string;
    customer_name: string;
    supervisor_id: number;
    run_instructions: string;
  }) => Promise<void>;
  isSubmitting: boolean;
}

export const StartRunForm: React.FC<StartRunFormProps> = ({
  supervisors,
  onStartRun,
  isSubmitting,
}) => {
  const [externalOrderId, setExternalOrderId] = useState(`ORD-${Math.floor(1000 + Math.random() * 9000)}`);
  const [customerName, setCustomerName] = useState("Jane Doe");
  const [selectedSupervisorId, setSelectedSupervisorId] = useState<number>(
    supervisors.length > 0 ? supervisors[0].id : 1
  );
  const [runInstructions, setRunInstructions] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!externalOrderId.trim()) {
      setErrorMsg("External Order ID is required.");
      return;
    }
    setErrorMsg("");
    try {
      await onStartRun({
        external_order_id: externalOrderId.trim(),
        customer_name: customerName.trim(),
        supervisor_id: selectedSupervisorId || (supervisors[0]?.id ?? 1),
        run_instructions: runInstructions.trim(),
      });
      // Generate new random Order ID for convenience
      setExternalOrderId(`ORD-${Math.floor(1000 + Math.random() * 9000)}`);
      setRunInstructions("");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to start supervision run.");
    }
  };

  const selectedSupervisor = supervisors.find((s) => s.id === selectedSupervisorId) || supervisors[0];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100">
      <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2 mb-4">
        <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Start Order Supervision Run
      </h2>

      {errorMsg && (
        <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs rounded-lg">
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        <div>
          <label className="block text-slate-300 font-medium mb-1">Supervisor Template</label>
          <select
            value={selectedSupervisorId}
            onChange={(e) => setSelectedSupervisorId(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            {supervisors.map((sup) => (
              <option key={sup.id} value={sup.id}>
                {sup.name} (ID: {sup.id})
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-slate-300 font-medium mb-1">External Order ID</label>
            <input
              type="text"
              value={externalOrderId}
              onChange={(e) => setExternalOrderId(e.target.value)}
              placeholder="e.g. ORD-1001"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>
          <div>
            <label className="block text-slate-300 font-medium mb-1">Customer Name</label>
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              placeholder="e.g. Alice Smith"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-slate-300 font-medium mb-1">
            Run-Specific Instructions <span className="text-slate-500 font-normal">(Optional)</span>
          </label>
          <textarea
            rows={2}
            value={runInstructions}
            onChange={(e) => setRunInstructions(e.target.value)}
            placeholder="e.g., Prioritize speed over cost. Escalations required for shipment delays."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
          />
        </div>

        {selectedSupervisor && (
          <div className="bg-slate-800/50 border border-slate-800 rounded-lg p-3 text-[11px] text-slate-400 space-y-1">
            <div>
              <span className="text-slate-300 font-medium">Model:</span> Llama 3.1:8b (Local Ollama)
            </div>
            <div>
              <span className="text-slate-300 font-medium">Base Instruction:</span> &quot;
              {selectedSupervisor.base_instruction}&quot;
            </div>
            <div>
              <span className="text-slate-300 font-medium">Allowed Tools:</span>{" "}
              {(selectedSupervisor.available_tools || selectedSupervisor.available_actions || [
                "message_fulfillment_team",
                "message_payments_team",
                "message_logistics_team",
                "message_customer",
                "create_internal_note",
              ]).join(", ")}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Starting Supervisor...
            </>
          ) : (
            "Start Supervision Run"
          )}
        </button>
      </form>
    </div>
  );
};
