# Architecture Note: AI-Powered Order Supervisor



## Overview & Core Principles

The AI-Powered Order Supervisor is an autonomous, event-driven order lifecycle monitoring and intervention platform. It combines durable workflow orchestration with local LLM-based operational decision-making.

### Core Architectural Principles
1. **One order = one long-running Temporal workflow.**  
   Each order run spawns a dedicated, long-running Temporal workflow instance (`order-supervisor-{order_id}`) that persists for the entire lifecycle of the order (from creation until delivery or manual termination).
2. **Temporal owns workflow orchestration and lifecycle, while the AI supervisor is responsible for operational decision-making.**  
   Temporal guarantees state persistence, signal queuing, sleep/wake timers, and fault-tolerant activity execution. The AI agent acts exclusively within Temporal Activity boundaries to evaluate context, select simulated business tools, and make operational decisions.

---

## System Components

### 1. Next.js Frontend Dashboard
- Built with **Next.js 16 (App Router)**, **React 19**, **TypeScript**, and **Tailwind CSS v4**.
- Provides real-time dashboard controls to launch supervision runs, inject order lifecycle events, issue run-specific operator instructions, execute live workflow controls (pause/resume/terminate), and inspect live timeline history and compact working memory.

### 2. FastAPI Backend Service
- Python 3.11 web service providing RESTful APIs for orders, supervisors, runs, events, instructions, and controls.
- Serves as the gateway between the frontend dashboard and both the PostgreSQL database and the Temporal Server.

### 3. Temporal Orchestration Server
- Manages durable execution, signal routing, timer scheduling, and activity retries.
- Communicates over gRPC (`localhost:7233`) with worker processes on task queue `order-supervisor`.

### 4. OrderSupervisorWorkflow
- Main Temporal workflow definition (`OrderSupervisorWorkflow`).
- Runs an event-loop that listens for signals, evaluates sleep/wake policies, invokes agent decision activities, executes business tool activities, and maintains run lifecycle state (`pending`, `active`, `sleeping`, `interrupted`, `completed`, `terminated`).

### 5. Temporal Signals
- **`event_signal`**: Ingests external order lifecycle events (e.g., payment failure, delay, customer message).
- **`pause_signal`**: Pauses supervisor decision-making while retaining incoming events in queue.
- **`resume_signal`**: Unblocks workflow execution and processes queued events.
- **`terminate_signal`**: Manually requests permanent workflow termination.
- **`schedule_wake_signal`**: Dynamically schedules or updates a Temporal wake-up timer.

### 6. Wake / Sleep Policy
- Pure, deterministic policy function (`evaluate_wake_sleep_policy`).
- Categorizes events into **WAKE** (high priority: `order_created`, `payment_failed`, `shipment_delayed`, `customer_message_received`, `refund_requested`, `delivered`) and **SLEEP** (low priority: `payment_confirmed`, `shipment_created`, `no_update_for_n_hours`).
- Prevents unnecessary LLM calls on routine status updates while ensuring instant wake-up on anomalies.

### 7. AI Supervisor Agent & Decision Engine
- Evaluates full context (order details, incoming event, compact memory, supervisor template instructions, run-specific instructions, available tools).
- Encapsulated inside Temporal Activity `execute_agent_decision_activity` to preserve Temporal workflow determinism.

### 8. Ollama + Llama Integration
- Primary LLM provider (`OllamaLLMProvider`) connects to a local Ollama instance running `llama3.1:8b` via HTTP API (`http://localhost:11434/api/chat`).
- Requests JSON-structured output enforcing exact tool parameters and reasoning.
- Automatically falls back to `MockLLMProvider` if Ollama is unreachable or during unit/integration test execution (`USE_MOCK_LLM=true`).

### 9. Simulated Business Tools & Actions
- **`message_fulfillment_team`**: Alerts warehouse/fulfillment staff regarding stock or packaging issues.
- **`message_payments_team`**: Escalates payment failures or refund requests.
- **`message_logistics_team`**: Queries carrier status or requests expedited shipment.
- **`message_customer`**: Sends proactive status updates or inquiries to the customer.
- **`create_internal_note`**: Logs operational notes to the order run record.
- **`no_action`**: Indicates routine event processing requiring no tool execution.

### 10. PostgreSQL Persistence Layer
- Managed via SQLAlchemy 2.0 with PostgreSQL.
- Schema consists of 6 primary models:
  - `Order`: Stores external order metadata and status.
  - `Supervisor`: Stores supervisor template configurations and base instructions.
  - `Run`: Stores workflow execution status (`RunStatus`), sleep timers, and Temporal workflow IDs.
  - `Activity`: Stores append-only chronological timeline records (`ActivityType`).
  - `Memory`: Stores compact working memory state.
  - `FinalSummary`: Stores post-run summaries and key learnings upon completion.

### 11. Compact Working Memory
- Capped at the 8 most recent key operational context entries.
- Summarizes historical events, actions taken, and wake reasons to prevent context window blowup and reduce LLM token overhead.

### 12. Timeline & Activity History Log
- Append-only event history tracking:
  - `incoming_event`
  - `wake_decision`
  - `sleep_decision`
  - `agent_action`
  - `manual_instruction`
  - `final_output`

### 13. Terminal Workflow States
- **`completed`**: Reached when a terminal event (`delivered`) is processed.
- **`terminated`**: Reached when an operator manually issues a `terminate_signal`.
- On entering a terminal state, final summary activities generate post-run retrospectives and workflow execution cleanly exits.
