"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  SupervisorTemplate,
  RunSummary,
  RunDetail,
  checkBackendHealth,
  fetchSupervisors,
  fetchRuns,
  fetchRunDetail,
  createOrder,
  createRun,
  sendEvent,
  addInstruction,
  interruptRun,
  resumeRun,
  terminateRun,
} from "../lib/api";
import { Header } from "../components/Header";
import { StartRunForm } from "../components/StartRunForm";
import { RunList } from "../components/RunList";
import { RunControlHeader } from "../components/RunControlHeader";
import { EventSimulator } from "../components/EventSimulator";
import { LiveInstructions } from "../components/LiveInstructions";
import { CompactMemoryView } from "../components/CompactMemoryView";
import { BusinessActionsView } from "../components/BusinessActionsView";
import { TimelineView } from "../components/TimelineView";

export default function DashboardPage() {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [supervisors, setSupervisors] = useState<SupervisorTemplate[]>([]);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [selectedRunDetail, setSelectedRunDetail] = useState<RunDetail | null>(null);
  const [isSubmittingRun, setIsSubmittingRun] = useState<boolean>(false);
  const [isSendingEvent, setIsSendingEvent] = useState<boolean>(false);
  const [isSubmittingInstruction, setIsSubmittingInstruction] = useState<boolean>(false);
  const [isControlActionLoading, setIsControlActionLoading] = useState<boolean>(false);
  const [globalNotification, setGlobalNotification] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  const showNotification = (type: "success" | "error", message: string) => {
    setGlobalNotification({ type, message });
    setTimeout(() => setGlobalNotification(null), 5000);
  };

  const loadData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await checkBackendHealth();
      setIsBackendOnline(true);

      const [sups, runList] = await Promise.all([
        fetchSupervisors().catch(() => []),
        fetchRuns().catch(() => []),
      ]);

      setSupervisors(sups);
      setRuns(runList);

      if (selectedRunId) {
        try {
          const detail = await fetchRunDetail(selectedRunId);
          setSelectedRunDetail(detail);
        } catch {
          setSelectedRunId(null);
          setSelectedRunDetail(null);
        }
      } else if (runList.length > 0 && !selectedRunId) {
        setSelectedRunId(runList[0].id);
        try {
          const detail = await fetchRunDetail(runList[0].id);
          setSelectedRunDetail(detail);
        } catch {
          // Ignore
        }
      }
    } catch {
      setIsBackendOnline(false);
    } finally {
      setIsRefreshing(false);
    }
  }, [selectedRunId]);

  useEffect(() => {
    loadData();
  }, []);

  // Polling loop every 3 seconds for active selected run
  useEffect(() => {
    if (!selectedRunId) return;

    const interval = setInterval(async () => {
      try {
        const runList = await fetchRuns();
        setRuns(runList);

        const detail = await fetchRunDetail(selectedRunId);
        setSelectedRunDetail(detail);

        // Stop polling if selected run reached terminal state
        if (detail.status === "completed" || detail.status === "terminated") {
          clearInterval(interval);
        }
      } catch {
        // Fail silently during background poll
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedRunId]);

  const handleSelectRun = async (runId: number) => {
    setSelectedRunId(runId);
    try {
      const detail = await fetchRunDetail(runId);
      setSelectedRunDetail(detail);
    } catch (err: any) {
      showNotification("error", err.message || "Failed to load run details.");
    }
  };

  const handleStartRun = async (data: {
    external_order_id: string;
    customer_name: string;
    supervisor_id: number;
    run_instructions: string;
  }) => {
    setIsSubmittingRun(true);
    try {
      const order = await createOrder(data.external_order_id, data.customer_name);
      const run = await createRun({
        order_id: order.id,
        supervisor_id: data.supervisor_id,
        run_instructions: data.run_instructions,
      });

      showNotification("success", `Supervision run #${run.id} started successfully!`);
      await loadData();
      await handleSelectRun(run.id);
    } catch (err: any) {
      showNotification("error", err.message || "Failed to start run.");
      throw err;
    } finally {
      setIsSubmittingRun(false);
    }
  };

  const handleSendEvent = async (eventType: string, payload: Record<string, unknown>) => {
    if (!selectedRunId) return;
    setIsSendingEvent(true);
    try {
      await sendEvent(selectedRunId, eventType, payload);
      showNotification("success", `Event signal '${eventType}' sent to Temporal workflow!`);
      const detail = await fetchRunDetail(selectedRunId);
      setSelectedRunDetail(detail);
    } catch (err: any) {
      showNotification("error", err.message || "Failed to inject event signal.");
      throw err;
    } finally {
      setIsSendingEvent(false);
    }
  };

  const handleAddInstruction = async (instruction: string) => {
    if (!selectedRunId) return;
    setIsSubmittingInstruction(true);
    try {
      await addInstruction(selectedRunId, instruction);
      showNotification("success", "Live instruction appended to run context!");
      const detail = await fetchRunDetail(selectedRunId);
      setSelectedRunDetail(detail);
    } catch (err: any) {
      showNotification("error", err.message || "Failed to add live instruction.");
      throw err;
    } finally {
      setIsSubmittingInstruction(false);
    }
  };

  const handleInterrupt = async () => {
    if (!selectedRunId) return;
    setIsControlActionLoading(true);
    try {
      await interruptRun(selectedRunId);
      showNotification("success", `Run #${selectedRunId} interrupted/paused.`);
      await loadData();
    } catch (err: any) {
      showNotification("error", err.message || "Failed to pause run.");
    } finally {
      setIsControlActionLoading(false);
    }
  };

  const handleResume = async () => {
    if (!selectedRunId) return;
    setIsControlActionLoading(true);
    try {
      await resumeRun(selectedRunId);
      showNotification("success", `Run #${selectedRunId} resumed.`);
      await loadData();
    } catch (err: any) {
      showNotification("error", err.message || "Failed to resume run.");
    } finally {
      setIsControlActionLoading(false);
    }
  };

  const handleTerminate = async () => {
    if (!selectedRunId) return;
    setIsControlActionLoading(true);
    try {
      await terminateRun(selectedRunId);
      showNotification("success", `Run #${selectedRunId} terminated.`);
      await loadData();
    } catch (err: any) {
      showNotification("error", err.message || "Failed to terminate run.");
    } finally {
      setIsControlActionLoading(false);
    }
  };

  const isSelectedRunTerminal =
    selectedRunDetail?.status === "completed" || selectedRunDetail?.status === "terminated";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      <Header
        isBackendOnline={isBackendOnline}
        onRefresh={loadData}
        isRefreshing={isRefreshing}
      />

      {globalNotification && (
        <div
          className={`px-6 py-3 text-xs font-medium flex items-center justify-between border-b ${
            globalNotification.type === "success"
              ? "bg-emerald-950/80 text-emerald-300 border-emerald-800"
              : "bg-rose-950/80 text-rose-300 border-rose-800"
          }`}
        >
          <span>{globalNotification.message}</span>
          <button onClick={() => setGlobalNotification(null)} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1600px] w-full mx-auto">
        {/* Left Column: Form & Run Selector (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <StartRunForm
            supervisors={supervisors}
            onStartRun={handleStartRun}
            isSubmitting={isSubmittingRun}
          />
          <RunList
            runs={runs}
            selectedRunId={selectedRunId}
            onSelectRun={handleSelectRun}
          />
        </div>

        {/* Right Column: Selected Run Details & Controls (8 cols) */}
        <div className="lg:col-span-8">
          {!selectedRunDetail ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400 flex flex-col items-center justify-center h-full">
              <svg className="w-12 h-12 text-slate-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
              </svg>
              <h3 className="text-base font-semibold text-slate-200">No Run Selected</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Select an existing run from the list on the left, or create a new order supervision run using the form.
              </p>
            </div>
          ) : (
            <div>
              <RunControlHeader
                run={selectedRunDetail}
                onInterrupt={handleInterrupt}
                onResume={handleResume}
                onTerminate={handleTerminate}
                isActionLoading={isControlActionLoading}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <EventSimulator
                    onSendEvent={handleSendEvent}
                    isSending={isSendingEvent}
                    disabled={isSelectedRunTerminal}
                  />
                  <LiveInstructions
                    onAddInstruction={handleAddInstruction}
                    isSubmitting={isSubmittingInstruction}
                    disabled={isSelectedRunTerminal}
                  />
                </div>

                <div>
                  {selectedRunDetail.memory && (
                    <CompactMemoryView
                      summary={selectedRunDetail.memory.summary}
                      updatedAt={selectedRunDetail.memory.updated_at}
                    />
                  )}
                  <BusinessActionsView activities={selectedRunDetail.activities || []} />
                </div>
              </div>

              <TimelineView activities={selectedRunDetail.activities || []} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
