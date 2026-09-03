# AI-Powered Order Supervisor

An event-driven, agentic order supervision platform powered by **Temporal**, **FastAPI**, **Next.js**, **PostgreSQL**, and local **Ollama (Llama 3.1 8B)**.

The system demonstrates how a long-running AI supervisor can continuously monitor an e-commerce order, react to lifecycle events, reason over operational context, execute business actions, maintain compact working memory, and generate a final operational summary.

---

## Overview

The **AI-Powered Order Supervisor** is a proof-of-concept platform for a long-running, stateful AI supervisor that monitors an individual e-commerce order throughout its complete fulfillment lifecycle.

Instead of relying on static rule engines or stateless API polling, each order supervision run is represented by a dedicated **Temporal Workflow** that remains active throughout the order lifecycle.

### Core Architectural Principle

> **One order = one long-running Temporal workflow.**

External lifecycle events and operational anomalies are delivered to the workflow using **Temporal Signals**.

The workflow evaluates each event using a deterministic **Wake/Sleep Policy**. When an event requires attention, the AI Supervisor Agent evaluates the current context, compact working memory, run-specific instructions, and incoming event before selecting an appropriate operational action.

Non-deterministic operations such as LLM inference and external tool execution are isolated inside **Temporal Activities**.

---

## Problem Statement

Modern e-commerce fulfillment involves multiple disconnected systems, including:

- Payment gateways
- Warehouse management systems
- Shipping carriers
- Customer support platforms
- Order management systems

Traditional automation approaches face several challenges.

### 1. Long-Running Processes

Orders may remain active for hours, days, or weeks.

Maintaining such processes using synchronous API requests, polling, or temporary background jobs can become fragile and difficult to recover.

### 2. Fragmented State and Context

Order information is distributed across multiple lifecycle events and systems.

Without persistent workflow state, important context can be lost between events, resulting in:

- Repeated actions
- Conflicting decisions
- Missing operational context
- Poor customer communication

### 3. Complex Exception Handling

Real-world situations frequently require contextual reasoning.

For example:

> A shipment is delayed while the customer simultaneously requests cancellation.

A rigid `IF-THEN` rule engine may struggle to determine the appropriate sequence of actions.

### Solution

This project combines:

- **Temporal** for durable workflow orchestration
- **FastAPI** for backend APIs
- **PostgreSQL** for persistent application state
- **Ollama / Llama 3.1 8B** for local AI reasoning
- **Next.js** for an interactive monitoring dashboard

The result is a long-running AI supervisor capable of monitoring an order from creation through delivery or termination.

---

# Key Features

## One Temporal Workflow Per Order

Each order supervision run receives a dedicated Temporal Workflow.

```text
order-supervisor-{order_id}
```

Example:

```text
order-supervisor-ORD-5001
```

The workflow maintains its own state throughout the order lifecycle.

---

## Event-Driven Supervision

External order lifecycle events are delivered to the workflow using Temporal Signals.

Supported events include:

```text
order_created
payment_confirmed
payment_failed
shipment_created
shipment_delayed
delivered
refund_requested
customer_message_received
no_update_for_n_hours
```

---

## AI-Driven Operational Decisions

The AI Supervisor evaluates:

- Current order state
- Incoming event
- Event history
- Compact working memory
- Run-specific instructions
- Operational context

The supervisor then selects an appropriate operational action.

---

## Deterministic Wake / Sleep Policy

The supervisor does not invoke the LLM for every event.

Events are classified into:

```text
WAKE
SLEEP
```

High-priority events trigger immediate AI assessment.

Low-priority events allow the workflow to remain dormant until another important event arrives or a scheduled timer fires.

---

## Scheduled Wake-Ups

Temporal timers allow the supervisor to wake automatically after a defined quiet period.

This enables supervision without continuous polling.

---

## Simulated Business Tools

The AI Supervisor can select from six simulated operational actions:

```text
message_fulfillment_team
message_payments_team
message_logistics_team
message_customer
create_internal_note
no_action
```

These actions currently record structured activity data in PostgreSQL rather than calling external business APIs.

---

## Compact Working Memory

The supervisor maintains a capped working memory of **8 items**.

This prevents uncontrolled growth of the LLM context while retaining important operational information.

```text
Maximum working memory: 8 items
```

---

## Timeline and Audit History

Every important workflow operation is recorded in an append-only timeline.

Examples include:

```text
incoming_event
wake_decision
sleep_decision
agent_action
manual_instruction
final_output
```

This provides an auditable history of supervisor decisions and operator interventions.

---

## Dynamic Run Instructions

Operators can inject instructions into an active supervision run.

Example:

```text
Prioritize customer response before contacting logistics.
```

The AI Supervisor incorporates these instructions into subsequent decisions.

---

## Live Run Controls

Operators can control active supervision runs through the dashboard.

Available controls:

```text
Pause
Resume
Interrupt
Inject Instruction
Terminate
```

Incoming events can continue to be queued while the supervisor is paused.

---

## Final Run Summary

When an order reaches a terminal state, the system generates a structured final summary containing:

- Final outcome
- Operational summary
- Key learnings
- Recommendations

---

## PostgreSQL Persistence

The system durably stores:

```text
Orders
Supervisors
Runs
Timeline Activities
Working Memory
Final Summaries
```

Persistence is implemented using **SQLAlchemy 2.0**.

---

# Architecture




# System Flow

```text
Order Created
      │
      ▼
Create Order Run
      │
      ▼
Start Temporal Workflow
      │
      ▼
OrderSupervisorWorkflow
      │
      ▼
Receive Event Signal
      │
      ▼
Wake / Sleep Policy
      │
      ├──────────────────┐
      │                  │
    SLEEP               WAKE
      │                  │
      ▼                  ▼
Wait / Timer        AI Supervisor
                         │
                         ▼
                  Select Action
                         │
                         ▼
                 Temporal Activity
                         │
                         ▼
                  Persist Result
                         │
                         ▼
                  Update Memory
                         │
                         ▼
                   Continue Run
                         │
                         ▼
                Delivered / Terminated
                         │
                         ▼
                   Final Summary
```

---

# Core Design Responsibility

> **Temporal handles workflow orchestration and lifecycle, while the AI Supervisor handles operational decision-making.**

The system deliberately separates deterministic orchestration from non-deterministic AI operations.

```text
┌─────────────────────────────┐
│     Temporal Workflow       │
│                             │
│  Signal Handling            │
│  State Transitions          │
│  Wake/Sleep Policy          │
│  Timers                     │
│  Queue Management            │
│  Lifecycle Control           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Temporal Activities      │
│                             │
│  LLM Inference              │
│  Database Persistence       │
│  Business Actions           │
└─────────────────────────────┘
```

This separation improves:

- Workflow determinism
- Replayability
- Fault tolerance
- Separation of responsibilities
- Operational reliability

---

# Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 16 | Interactive supervision dashboard |
| Frontend Language | TypeScript | Type-safe frontend development |
| UI | React 19 | Dashboard components |
| Styling | Tailwind CSS v4 | Frontend styling |
| Backend | Python 3.11 | Backend and workflow services |
| API | FastAPI | RESTful API layer |
| Server | Uvicorn | ASGI application server |
| Workflow | Temporal | Durable workflow orchestration |
| Workflow SDK | `temporalio` | Python Temporal SDK |
| AI Runtime | Ollama | Local LLM runtime |
| LLM | Llama 3.1 8B | AI supervisor reasoning |
| Database | PostgreSQL | Persistent application state |
| ORM | SQLAlchemy 2.0 | Database access layer |
| Validation | Pydantic | Request/response validation |
| Testing | Pytest | Automated testing |
| Async Testing | pytest-asyncio | Async test support |

---

# Project Structure

```text
Order_Supervisor_project/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── orders.py
│   │   │   ├── runs.py
│   │   │   └── supervisors.py
│   │   │
│   │   ├── models/
│   │   │   ├── order.py
│   │   │   ├── run.py
│   │   │   ├── activity.py
│   │   │   ├── memory.py
│   │   │   └── final_summary.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── event.py
│   │   │   ├── order.py
│   │   │   ├── run.py
│   │   │   └── supervisor.py
│   │   │
│   │   ├── services/
│   │   │   ├── agent.py
│   │   │   ├── order_service.py
│   │   │   ├── run_service.py
│   │   │   ├── temporal_service.py
│   │   │   └── llm_provider.py
│   │   │
│   │   ├── database.py
│   │   ├── init_db.py
│   │   └── main.py
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── database/
│   └── migrations/
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── architecture.png
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   └── ...
│   │
│   ├── components/
│   │   ├── EventSimulator.tsx
│   │   ├── TimelineView.tsx
│   │   ├── MemoryView.tsx
│   │   └── ...
│   │
│   ├── lib/
│   │   └── api.ts
│   │
│   ├── package.json
│   └── tsconfig.json
│
├── temporal/
│   ├── activities/
│   │   ├── agent.py
│   │   ├── persistence.py
│   │   └── tools.py
│   │
│   ├── policies/
│   │   └── wake_sleep_policy.py
│   │
│   ├── workflows/
│   │   └── order_supervisor.py
│   │
│   ├── client.py
│   └── worker.py
│
├── tests/
│   ├── test_events.py
│   ├── test_policies.py
│   ├── test_workflows.py
│   ├── test_activities.py
│   └── ...
│
├── .env.example
├── .gitignore
└── README.md
```

---

# Workflow Architecture

Each supervision run receives a unique Temporal Workflow ID:

```text
order-supervisor-{order_id}
```

Example:

```text
order-supervisor-ORD-5001
```

The workflow remains alive throughout the order lifecycle.

---

# Temporal Signals

## `event_signal`

Receives external order lifecycle events.

```python
event_signal(event)
```

---

## `pause_signal`

Pauses supervisor decision-making while retaining incoming events.

```python
pause_signal()
```

---

## `resume_signal`

Resumes processing of queued events.

```python
resume_signal()
```

---

## `terminate_signal`

Requests workflow termination.

```python
terminate_signal()
```

---

## `schedule_wake_signal`

Updates the scheduled workflow wake-up timer.

```python
schedule_wake_signal(...)
```

---

# Wake / Sleep Policy

The deterministic Wake/Sleep Policy prevents unnecessary AI inference.

## WAKE Events

The following events trigger immediate supervisor assessment:

```text
order_created
payment_failed
shipment_delayed
customer_message_received
refund_requested
delivered
```

## SLEEP Events

The following events allow the workflow to remain dormant:

```text
payment_confirmed
shipment_created
no_update_for_n_hours
```

### Example

```text
payment_confirmed
       │
       ▼
   SLEEP decision
       │
       ▼
Workflow waits
       │
       ▼
shipment_delayed
       │
       ▼
   WAKE decision
       │
       ▼
AI Supervisor
```

---

# AI Supervisor Integration

The AI layer is implemented through a provider abstraction.

```text
backend/app/services/llm_provider.py
```

Two providers are supported.

---

## OllamaLLMProvider

Connects to a local Ollama server:

```text
http://localhost:11434/api/chat
```

Configured model:

```text
llama3.1:8b
```

The provider is instructed to return structured JSON matching the application's `AgentDecision` schema.

---

## MockLLMProvider

A deterministic provider used for:

- Automated testing
- Offline development
- CI environments
- Debugging
- Development without Ollama

Mock mode can be enabled with:

```env
USE_MOCK_LLM=true
```

---

# Available Events

The system currently supports **9 event types**.

| Event | Description | Behavior |
|---|---|---|
| `order_created` | New order created | WAKE |
| `payment_confirmed` | Payment successfully processed | SLEEP |
| `payment_failed` | Payment processing failed | WAKE |
| `shipment_created` | Shipment created | SLEEP |
| `shipment_delayed` | Shipment delayed | WAKE |
| `delivered` | Order delivered | WAKE / Terminal |
| `refund_requested` | Customer requests refund | WAKE |
| `customer_message_received` | Customer sends message | WAKE |
| `no_update_for_n_hours` | No operational update | SLEEP |

---

# Available Business Actions

The AI Supervisor can select six operational actions.

| Action | Purpose |
|---|---|
| `message_fulfillment_team` | Notify fulfillment operations |
| `message_payments_team` | Notify payment operations |
| `message_logistics_team` | Notify logistics operations |
| `message_customer` | Send customer-facing communication |
| `create_internal_note` | Record an internal operational note |
| `no_action` | No intervention required |

> These are simulated tools in the current proof of concept.

---

# Working Memory

The supervisor maintains compact working memory to avoid continuously expanding the LLM context.

Maximum capacity:

```text
8 items
```

Example:

```text
1. Order created successfully
2. Payment failed with DECLINED
3. Payments team notified
4. Shipment delayed
5. Logistics team notified
6. Customer requested status update
7. Customer communication prioritized
8. Delivery completed
```

The memory is intentionally bounded so that the LLM receives a compact operational context.

---

# Timeline and Activity History

The system maintains an append-only operational timeline.

Supported activity types include:

```text
incoming_event
wake_decision
sleep_decision
agent_action
manual_instruction
final_output
```

Example:

```text
10:02:01  incoming_event
10:02:01  wake_decision
10:02:02  agent_action
10:02:02  memory_updated
10:05:17  manual_instruction
10:05:19  agent_action
10:15:43  incoming_event
10:15:44  final_output
```

---

# Run Lifecycle

A supervision run can transition through the following states:

```text
PENDING
   │
   ▼
ACTIVE
   │
   ├────────────────┐
   │                │
   ▼                ▼
SLEEPING       INTERRUPTED
   │                │
   └───────┬────────┘
           │
           ▼
         ACTIVE
           │
           ├────────────────┐
           │                │
           ▼                ▼
      COMPLETED        TERMINATED
```

Supported states:

```text
pending
active
sleeping
interrupted
completed
terminated
```

---

# Database Schema

PostgreSQL is used for durable application persistence.

## `orders`

Stores order-level information.

```text
orders
├── external_order_id
├── customer_name
└── order_status
```

---

## `supervisors`

Stores reusable supervisor configurations.

```text
supervisors
├── name
├── description
└── base_instruction
```

---

## `runs`

Stores individual supervision runs.

```text
runs
├── order_id
├── state
├── run_instructions
├── workflow_id
└── timestamps
```

---

## `activities`

Stores chronological operational timeline records.

```text
activities
├── incoming_event
├── wake_decision
├── sleep_decision
├── agent_action
├── manual_instruction
└── final_output
```

---

## `memories`

Stores compact supervisor working memory.

```text
memories
├── run_id
├── memory_items
└── timestamps
```

---

## `final_summaries`

Stores final run output.

```text
final_summaries
├── run_id
├── final_summary
├── key_learnings
├── recommendations
└── created_at
```

---

# Environment Configuration

Create a local environment file:

```bash
cp .env.example backend/.env
```

Update the configuration:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/order_supervisor

TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TASK_QUEUE=order-supervisor

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

USE_MOCK_LLM=false
```

> Never commit `.env` files containing passwords, API keys, or other secrets.

---

# Prerequisites

Install the following:

- Python 3.11+
- Node.js 18+
- npm
- PostgreSQL
- Temporal CLI
- Ollama (optional when using Mock LLM)

For live AI execution, download the model:

```bash
ollama pull llama3.1:8b
```

---

# Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Order_Supervisor_project
```

---

## 2. Create Python Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Backend Dependencies

From the project root:

```bash
pip install -r backend/requirements.txt
```

---

## 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 5. Configure Environment

```bash
cp .env.example backend/.env
```

Update the database credentials and other settings.

---

# Database Initialization

Make sure PostgreSQL is running.

Create the database:

```sql
CREATE DATABASE order_supervisor;
```

Initialize the application schema:

```bash
python -m backend.app.init_db
```

---

# Running the Application

The application consists of multiple services.

Run each service in a separate terminal.

---

## 1. Start Temporal Server

```bash
temporal server start-dev
```

Temporal Server:

```text
localhost:7233
```

Temporal Web UI:

```text
http://localhost:8233
```

---

## 2. Start Ollama

Skip this step when using Mock LLM mode.

```bash
ollama run llama3.1:8b
```

Ollama API:

```text
http://localhost:11434
```

---

## 3. Start FastAPI Backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

OpenAPI specification:

```text
http://localhost:8000/openapi.json
```

---

## 4. Start Temporal Worker

From the project root:

```bash
python -m temporal.worker
```

The worker listens on:

```text
order-supervisor
```

---

## 5. Start Next.js Frontend

```bash
cd frontend
npm run dev
```

Dashboard:

```text
http://localhost:3000
```

---

# Testing

Run the complete automated test suite:

```bash
python -m pytest tests/
```

Current verified baseline:

```text
60 passed
0 failures
```

The test suite covers areas including:

- Event schemas
- Wake/Sleep policies
- Temporal workflows
- Temporal Signals
- Temporal Activities
- Persistence
- Agent behavior
- Mock LLM integration
- Workflow lifecycle
- Run state transitions

---

# Demonstration Walkthrough

The following scenario demonstrates the complete supervision lifecycle.

---

## Step 1 — Create a Supervision Run

Open:

```text
http://localhost:3000
```

Select:

```text
Order Supervisor
```

Create a supervision run for:

```text
ORD-5001
```

Expected initial state:

```text
ACTIVE
```

---

## Step 2 — Order Creation

The workflow starts and records the initial order state.

The timeline should contain an incoming event and an initial supervisor action.

Example:

```text
incoming_event
agent_action
```

Compact memory should also be updated.

---

## Step 3 — Simulate Payment Failure

Inject:

```text
payment_failed
```

Example payload:

```json
{
  "gateway_code": "DECLINED"
}
```

Expected flow:

```text
payment_failed
       │
       ▼
     WAKE
       │
       ▼
AI Supervisor
       │
       ▼
message_payments_team
```

The timeline should record:

```text
incoming_event
wake_decision
agent_action
```

---

## Step 4 — Pause the Run

Click:

```text
Pause Run
```

Then inject:

```text
shipment_delayed
```

The event should remain queued while the supervisor is interrupted.

Expected state:

```text
INTERRUPTED
```

---

## Step 5 — Resume the Run

Click:

```text
Resume Run
```

The workflow resumes processing queued events.

The delayed shipment event should trigger:

```text
WAKE
```

The AI Supervisor can select:

```text
message_logistics_team
```

---

## Step 6 — Inject a Live Instruction

Add the following instruction:

```text
Inform customer about delivery delay immediately.
```

The instruction becomes part of the run context.

Timeline:

```text
manual_instruction
```

---

## Step 7 — Simulate Customer Message

Inject:

```text
customer_message_received
```

Example payload:

```json
{
  "message": "Where is my order?"
}
```

Expected flow:

```text
customer_message_received
            │
            ▼
          WAKE
            │
            ▼
      AI Supervisor
            │
            ▼
     message_customer
```

The supervisor should incorporate the live instruction when selecting its response.

---

## Step 8 — Complete the Order

Inject:

```text
delivered
```

Example payload:

```json
{
  "signed_by": "Customer"
}
```

Expected result:

```text
ACTIVE
  │
  ▼
delivered
  │
  ▼
COMPLETED
  │
  ▼
Final Summary
```

The final output should contain:

- Final outcome
- Operational summary
- Key learnings
- Recommendations

---

# Example End-to-End Flow

```text
┌───────────────────┐
│   ORDER CREATED   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Temporal Workflow │
│      ACTIVE       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  PAYMENT FAILED   │
└─────────┬─────────┘
          │
          ▼
        WAKE
          │
          ▼
┌───────────────────┐
│   AI SUPERVISOR   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Payments Team     │
│ Notification      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Shipment Delayed  │
└─────────┬─────────┘
          │
          ▼
        WAKE
          │
          ▼
┌───────────────────┐
│ Logistics Team    │
│ Notification      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Customer Message  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   AI SUPERVISOR   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Customer Response │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│     DELIVERED     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│     COMPLETED     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   FINAL SUMMARY   │
└───────────────────┘
```

---

# Determinism and Temporal Safety

A central design principle of this project is keeping non-deterministic operations outside the Temporal Workflow definition.

The workflow itself performs deterministic operations such as:

```text
Signal handling
State transitions
Event classification
Timers
Queue management
Workflow lifecycle
```

LLM inference and business actions are executed through Temporal Activities.

```text
┌────────────────────────────┐
│      Temporal Workflow     │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│      Temporal Activity     │
├────────────────────────────┤
│                            │
│  LLM Inference             │
│  Database Persistence      │
│  Business Tool Execution   │
│                            │
└────────────────────────────┘
```

This architecture improves:

- Replayability
- Fault tolerance
- Workflow determinism
- Separation of responsibilities
- Operational reliability

---

# Why Temporal?

Traditional approaches often rely on:

```text
Cron Jobs
Polling
Background Workers
Scheduled API Calls
```

These approaches become increasingly difficult to manage when processes are long-running and stateful.

Temporal provides:

- Durable execution
- Workflow state persistence
- Signals
- Timers
- Retries
- Activity execution
- Failure recovery
- Workflow observability

This makes Temporal well suited for order supervision workflows that remain active for extended periods.

---

# Why a Local LLM?

The project intentionally uses a local LLM through Ollama.

Benefits include:

- No external LLM API dependency
- Local development
- Reduced external data exposure
- Offline testing capability
- Reproducible development environment
- Easy provider replacement

The architecture also supports a `MockLLMProvider`, allowing the system to operate without an LLM during automated testing.

---

# Design Principles

## 1. One Order, One Workflow

Each order supervision run receives an isolated workflow.

## 2. Event-Driven Instead of Polling

Events wake the workflow rather than continuously polling external systems.

## 3. Deterministic Orchestration

Temporal owns workflow lifecycle and deterministic state management.

## 4. AI for Decisions, Not Orchestration

The LLM selects operational actions but does not directly control workflow execution.

## 5. Activities for Side Effects

Database writes, LLM calls, and business actions occur inside Temporal Activities.

## 6. Compact Context

Working memory is explicitly bounded to prevent uncontrolled context growth.

## 7. Human-in-the-Loop

Operators can pause, resume, terminate, and inject instructions into live runs.

## 8. Full Auditability

Important operational decisions are recorded in a persistent timeline.

---

# Current Limitations

This project is currently a **proof of concept**.

## Simulated Business Integrations

Business actions currently write structured records to PostgreSQL rather than calling real services.

For example:

```text
message_payments_team
```

does not currently send a real message to a payment provider.

---

## Local LLM Performance

Ollama inference latency depends on:

- CPU
- GPU
- Available RAM
- Model configuration
- Host hardware

---

## Single Task Queue

The current implementation uses one Temporal task queue:

```text
order-supervisor
```

---

## Single-Order Workflow Model

The current POC focuses on one workflow per order rather than large-scale production deployment.

---

# Future Improvements

## Production Integrations

Integrate real external systems such as:

```text
Shopify
Stripe
FedEx
UPS
DHL
Customer Support APIs
Warehouse Management Systems
```

---

## Multi-Agent Architecture

Introduce specialized agents:

```text
                  ┌──────────────────┐
                  │  AI Supervisor   │
                  └────────┬─────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │  Payments  │ │ Logistics  │ │  Customer  │
      │   Agent    │ │   Agent    │ │   Agent    │
      └────────────┘ └────────────┘ └────────────┘
```

Each specialized agent could handle a dedicated operational domain.

---

## Temporal Schedules

Use Temporal Schedules for recurring operational processes such as:

- Reconciliation
- Periodic order health checks
- SLA monitoring
- Batch processing

---

## Production Observability

Future versions could integrate:

- Metrics
- Distributed tracing
- Structured logging
- OpenTelemetry
- Alerting
- Production monitoring

---

## External Event Webhooks

Replace manual event simulation with real webhook integrations.

```text
Payment Gateway
       │
       ▼
   Webhook
       │
       ▼
    FastAPI
       │
       ▼
Temporal Signal
       │
       ▼
Order Supervisor
```

---

# Security Considerations

For production deployment:

- Store secrets using a secret manager
- Never commit `.env` files
- Authenticate API requests
- Authorize operator actions
- Validate incoming webhook signatures
- Encrypt sensitive database fields where required
- Restrict Temporal access
- Apply API rate limiting
- Audit manual operator instructions

---

# Development Notes

Python cache directories such as:

```text
__pycache__/
```

are automatically generated by Python and should not be committed to Git.

Recommended `.gitignore` entries:

```gitignore
__pycache__/
*.py[cod]

.venv/
venv/

.env

*.log

.pytest_cache/
.mypy_cache/

node_modules/
.next/

.DS_Store
```

Environment templates such as:

```text
.env.example
```

should be committed because they document required configuration without exposing secrets.

---

# API Documentation

Once the backend is running, interactive API documentation is available at:

```text
http://localhost:8000/docs
```

OpenAPI specification:

```text
http://localhost:8000/openapi.json
```

---

# Project Status

```text
Status           : Proof of Concept
Test Suite       : 60 passed
Failures         : 0
Workflow Engine  : Temporal
LLM              : Ollama / Llama 3.1 8B
Database         : PostgreSQL
Backend          : FastAPI
Frontend         : Next.js
```

---

# Learning Objectives

This project demonstrates practical experience with:

- Durable workflow orchestration
- Event-driven architectures
- Temporal Signals
- Temporal Activities
- Temporal Timers
- Long-running workflows
- AI agent integration
- Local LLM inference
- Structured LLM outputs
- Human-in-the-loop systems
- PostgreSQL persistence
- SQLAlchemy
- FastAPI
- Next.js
- TypeScript
- Automated testing
- Workflow determinism
- Fault-tolerant system design

---

# Use Cases

The architecture can be adapted beyond e-commerce.

## Customer Support

Long-running AI supervision of customer support cases.

## Logistics

Monitoring shipments and reacting to delivery delays.

## Payments

Supervising payment failures and reconciliation.

## Insurance

Tracking claims through multiple processing stages.

## Healthcare Operations

Supervising administrative workflows and operational events.

## Enterprise Operations

Monitoring long-running business processes across multiple systems.

---

# License

This project is intended as a proof-of-concept and learning/research project.

Add an appropriate license before public production use.

---

# Author

**Lakshitha Annadurai**

Computer Science & Engineering  
AI / Machine Learning / Data Science

- GitHub: https://github.com/lakshiii
- LinkedIn: https://linkedin.com/in/lakshitha05

---

# Acknowledgements

Built using:

- Temporal
- FastAPI
- Next.js
- PostgreSQL
- SQLAlchemy
- Ollama
- Llama 3.1
- Pytest
- React
- TypeScript
- Tailwind CSS

---

# Project Summary

> **AI-Powered Order Supervisor is a long-running, event-driven AI system where Temporal provides durable workflow orchestration and a local LLM provides contextual operational decision-making.**

The project demonstrates how AI agents can be integrated into reliable workflow infrastructure without allowing non-deterministic LLM behavior to compromise workflow determinism.

```text
              ┌─────────────────────────┐
              │     E-Commerce Order    │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    Temporal Workflow    │
              │                         │
              │  Durable + Stateful     │
              └────────────┬────────────┘
                           │
                    Events / Signals
                           │
                           ▼
              ┌─────────────────────────┐
              │    Wake/Sleep Policy    │
              └────────────┬────────────┘
                           │
                          WAKE
                           │
                           ▼
              ┌─────────────────────────┐
              │     AI Supervisor       │
              │     Llama 3.1 8B        │
              └────────────┬────────────┘
                           │
                     Tool Selection
                           │
                           ▼
              ┌─────────────────────────┐
              │   Business Activities  │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │       PostgreSQL        │
              │                         │
              │ Timeline + Memory       │
              │ Runs + Summaries        │
              └─────────────────────────┘
```

---

**Built as a practical demonstration of combining durable workflow orchestration with agentic AI decision-making.**
