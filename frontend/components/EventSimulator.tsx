"use client";

import React, { useState } from "react";

interface EventSimulatorProps {
  onSendEvent: (eventType: string, payload: Record<string, unknown>) => Promise<void>;
  isSending: boolean;
  disabled: boolean;
}

const SUPPORTED_EVENTS = [
  "payment_failed",
  "shipment_delayed",
  "customer_message_received",
  "refund_requested",
  "payment_confirmed",
  "shipment_created",
  "delivered",
  "order_created",
];

const PRESETS: Record<string, Record<string, unknown>> = {
  payment_failed: { gateway_code: "CARD_DECLINED", reason: "Insufficient funds" },
  shipment_delayed: { reason: "Severe weather delay", delay_hours: 24 },
  customer_message_received: { message: "Where is my package? Is there any update on delivery?" },
  refund_requested: { reason: "Customer requested refund due to delivery delay" },
  payment_confirmed: { payment_id: "PAY-8829103", amount: 149.99 },
  shipment_created: { tracking_number: "TRK-90021", carrier: "Express Delivery" },
  delivered: { signed_by: "Customer" },
  order_created: { item: "Supervision License" },
};

export const EventSimulator: React.FC<EventSimulatorProps> = ({ onSendEvent, isSending, disabled }) => {
  const [eventType, setEventType] = useState("payment_failed");
  const [payloadJson, setPayloadJson] = useState(JSON.stringify(PRESETS["payment_failed"], null, 2));
  const [jsonError, setJsonError] = useState("");

  const handleSelectEventType = (type: string) => {
    setEventType(type);
    const preset = PRESETS[type] || {};
    setPayloadJson(JSON.stringify(preset, null, 2));
    setJsonError("");
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setJsonError("");

    let parsed: Record<string, unknown> = {};
    try {
      if (payloadJson.trim()) {
        parsed = JSON.parse(payloadJson);
      }
    } catch (err: any) {
      setJsonError("Invalid JSON syntax: " + err.message);
      return;
    }

    try {
      await onSendEvent(eventType, parsed);
    } catch (err: any) {
      setJsonError(err.message || "Failed to inject event.");
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm text-slate-100 mb-6">
      <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-3">
        <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
        Event Simulator (Inject Event Signal)
      </h3>

      {jsonError && (
        <div className="mb-3 p-2.5 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs rounded-lg">
          {jsonError}
        </div>
      )}

      <form onSubmit={handleSend} className="space-y-3 text-xs">
        <div>
          <label className="block text-slate-300 font-medium mb-1">Select Event Type</label>
          <select
            value={eventType}
            onChange={(e) => handleSelectEventType(e.target.value)}
            disabled={disabled}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500 font-mono disabled:opacity-50"
          >
            {SUPPORTED_EVENTS.map((evt) => (
              <option key={evt} value={evt}>
                {evt}
              </option>
            ))}
          </select>
        </div>

        {/* Quick Presets */}
        <div>
          <label className="block text-slate-400 text-[11px] font-medium mb-1">Quick Presets</label>
          <div className="flex flex-wrap gap-1.5">
            {Object.keys(PRESETS).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => handleSelectEventType(type)}
                disabled={disabled}
                className={`text-[10px] px-2 py-1 rounded font-mono border transition-colors ${
                  eventType === type
                    ? "bg-indigo-600/30 text-indigo-300 border-indigo-500/50"
                    : "bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200"
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Payload JSON Textarea */}
        <div>
          <label className="block text-slate-300 font-medium mb-1">Event Payload JSON</label>
          <textarea
            rows={4}
            value={payloadJson}
            onChange={(e) => setPayloadJson(e.target.value)}
            disabled={disabled}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 font-mono text-indigo-300 text-xs focus:outline-none focus:border-indigo-500 disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={isSending || disabled}
          className="w-full bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
        >
          {isSending ? (
            <>
              <svg className="animate-spin w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Injecting Signal to Temporal...
            </>
          ) : (
            "Inject Event Signal"
          )}
        </button>
      </form>
    </div>
  );
};
