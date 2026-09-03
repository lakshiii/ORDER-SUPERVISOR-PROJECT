const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface SupervisorTemplate {
  id: number;
  name: string;
  base_instruction: string;
  available_actions?: string[];
  available_tools?: string[];
  default_wake_behavior?: string;
  model_config?: Record<string, unknown>;
  aggressiveness?: number;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: number;
  external_order_id: string;
  customer_name?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Activity {
  id: number;
  run_id: number;
  type: string;
  source: string;
  content: string;
  activity_metadata?: Record<string, unknown>;
  created_at: string;
}

export interface Memory {
  id: number;
  run_id: number;
  summary: string;
  current_status: string;
  updated_at: string;
}

export interface FinalSummary {
  id: number;
  run_id: number;
  summary: string;
  learnings?: string;
  feedback?: string;
  created_at: string;
}

export interface RunSummary {
  id: number;
  order_id: number;
  supervisor_id: number;
  temporal_workflow_id?: string;
  status: string;
  current_status: string;
  run_instructions?: string;
  sleep_until?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface RunDetail extends RunSummary {
  order?: Order;
  supervisor?: SupervisorTemplate;
  memory?: Memory;
  final_summary?: FinalSummary;
  activities: Activity[];
}

export interface EventResponse {
  run_id: number;
  event_type: string;
  status: string;
  timestamp: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP error ${res.status}`;
    try {
      const data = await res.json();
      if (data && data.detail) {
        errorDetail = data.detail;
      }
    } catch {
      // Ignore JSON parse error if response body is empty or non-JSON
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export async function checkBackendHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_BASE_URL}/`, { cache: "no-store" });
  return handleResponse(res);
}

export async function fetchSupervisors(): Promise<SupervisorTemplate[]> {
  const res = await fetch(`${API_BASE_URL}/api/supervisors`, { cache: "no-store" });
  return handleResponse(res);
}

export async function fetchOrders(): Promise<Order[]> {
  const res = await fetch(`${API_BASE_URL}/api/orders`, { cache: "no-store" });
  return handleResponse(res);
}

export async function createOrder(external_order_id: string, customer_name?: string): Promise<Order> {
  const res = await fetch(`${API_BASE_URL}/api/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ external_order_id, customer_name }),
  });
  return handleResponse(res);
}

export async function fetchRuns(): Promise<RunSummary[]> {
  const res = await fetch(`${API_BASE_URL}/api/runs`, { cache: "no-store" });
  return handleResponse(res);
}

export async function fetchRunDetail(runId: number): Promise<RunDetail> {
  const res = await fetch(`${API_BASE_URL}/api/runs/${runId}`, { cache: "no-store" });
  return handleResponse(res);
}

export async function createRun(data: {
  order_id: number;
  supervisor_id: number;
  run_instructions?: string;
}): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function sendEvent(runId: number, event_type: string, payload: Record<string, unknown>): Promise<EventResponse> {
  const res = await fetch(`${API_BASE_URL}/api/runs/${runId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_type, payload }),
  });
  return handleResponse(res);
}

export async function addInstruction(runId: number, instruction: string): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/api/runs/${runId}/instructions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instruction }),
  });
  return handleResponse(res);
}

export async function interruptRun(runId: number): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/api/runs/${runId}/interrupt`, {
    method: "POST",
  });
  return handleResponse(res);
}

export async function resumeRun(runId: number): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/api/runs/${runId}/resume`, {
    method: "POST",
  });
  return handleResponse(res);
}

export async function terminateRun(runId: number): Promise<RunSummary> {
  const res = await fetch(`${API_BASE_URL}/api/runs/${runId}/terminate`, {
    method: "POST",
  });
  return handleResponse(res);
}
