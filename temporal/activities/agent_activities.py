import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from temporalio import activity
import backend.app.database as db_module
from backend.app.models.run import Run
from backend.app.models.order import Order
from backend.app.models.supervisor import Supervisor
from backend.app.models.activity import Activity
from backend.app.models.memory import Memory
from backend.app.models.enums import ActivityType
from backend.app.schemas.agent import (
    AgentContextInput,
    AgentDecision,
    ToolExecutionResult,
    ALLOWED_BUSINESS_TOOLS,
)
from backend.app.services.agent_service import evaluate_agent_decision
from temporal.activities.persistence import save_activity_event

logger = logging.getLogger("agent_activities")

@dataclass
class ExecuteAgentInput:
    run_id: int
    order_id: int
    event_type: str
    event_payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BusinessToolInput:
    run_id: int
    order_id: int
    action: str
    action_payload: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

@activity.defn
async def execute_agent_decision_activity(input: ExecuteAgentInput) -> AgentDecision:
    """
    Temporal Activity boundary for AI Agent context fetching and LLM decision reasoning.
    Runs outside deterministic workflow code.
    """
    logger.info(
        "Activity execute_agent_decision: Run ID %s, Order ID %s, Event '%s'",
        input.run_id,
        input.order_id,
        input.event_type,
    )

    # 1. Fetch DB context & compact memory in a short-lived session
    db = db_module.SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == input.run_id).first()
        order = db.query(Order).filter(Order.id == input.order_id).first()
        supervisor = db.query(Supervisor).filter(Supervisor.id == run.supervisor_id).first() if run else None
        memory = db.query(Memory).filter(Memory.run_id == input.run_id).first()
        activities = (
            db.query(Activity)
            .filter(Activity.run_id == input.run_id)
            .order_by(Activity.created_at.desc())
            .limit(10)
            .all()
            if run
            else []
        )

        recent_timeline = [
            {
                "type": a.type,
                "source": a.source,
                "content": a.content,
                "created_at": a.created_at.isoformat() if a.created_at else "",
            }
            for a in activities
        ]

        current_status = order.status if order else "unknown"
        supervisor_name = supervisor.name if supervisor else "Default Supervisor"
        base_instruction = supervisor.base_instruction if supervisor else ""
        run_instructions = run.run_instructions if run else None
        compact_memory_summary = memory.summary if memory else ""
        available_tools = (
            supervisor.available_tools
            if (supervisor and supervisor.available_tools)
            else ALLOWED_BUSINESS_TOOLS
        )
    finally:
        db.close()

    # 2. Evaluate LLM decision outside DB session
    context = AgentContextInput(
        run_id=input.run_id,
        order_id=input.order_id,
        event_type=input.event_type,
        event_payload=input.event_payload,
        current_order_status=current_status,
        supervisor_name=supervisor_name,
        base_instruction=base_instruction,
        run_instructions=run_instructions,
        compact_memory_summary=compact_memory_summary,
        available_tools=available_tools,
        recent_timeline=recent_timeline,
    )

    try:
        decision = evaluate_agent_decision(context)
    except Exception as e:
        logger.error("Error evaluating agent decision: %s", e)
        decision = AgentDecision(
            action="create_internal_note",
            reasoning=f"Agent evaluation error: {e}",
            action_payload={"error": str(e)},
        )

    # 3. Log decision into activities timeline table via save_activity_event helper
    save_activity_event(
        run_id=input.run_id,
        type_str=ActivityType.AGENT_ACTION.value,
        source="ai_supervisor_agent",
        content=f"Agent selected action '{decision.action}': {decision.reasoning}",
        metadata={
            "action": decision.action,
            "reasoning": decision.reasoning,
            "action_payload": decision.action_payload,
            "needs_future_wake": decision.needs_future_wake,
            "recommended_wake_seconds": decision.recommended_wake_seconds,
        },
    )

    return decision

@activity.defn
async def execute_business_tool_activity(input: BusinessToolInput) -> ToolExecutionResult:
    """
    Temporal Activity boundary for simulated business tool execution.
    Runs outside deterministic workflow code.
    """
    logger.info(
        "Activity execute_business_tool: Run ID %s, Action '%s', Payload: %s",
        input.run_id,
        input.action,
        input.action_payload,
    )
    action_clean = input.action.strip().lower()

    # Simulated Tool Messages
    tool_messages = {
        "message_fulfillment_team": f"[Simulated Tool Execution] Message sent to Fulfillment Team for Order #{input.order_id}: {input.reasoning}",
        "message_payments_team": f"[Simulated Tool Execution] Message sent to Payments Team for Order #{input.order_id}: {input.reasoning}",
        "message_logistics_team": f"[Simulated Tool Execution] Message sent to Logistics Team for Order #{input.order_id}: {input.reasoning}",
        "message_customer": f"[Simulated Tool Execution] Status notification sent to Customer for Order #{input.order_id}: {input.reasoning}",
        "create_internal_note": f"[Simulated Tool Execution] Internal Note logged for Order #{input.order_id}: {input.reasoning}",
    }

    msg = tool_messages.get(
        action_clean,
        f"[Simulated Tool Execution] Executed tool '{action_clean}' for Order #{input.order_id}.",
    )

    # Log simulated tool execution to activities timeline table via save_activity_event helper
    save_activity_event(
        run_id=input.run_id,
        type_str=ActivityType.AGENT_ACTION.value,
        source="business_tool",
        content=msg,
        metadata={
            "action": action_clean,
            "action_payload": input.action_payload,
            "reasoning": input.reasoning,
            "status": "success",
        },
    )

    return ToolExecutionResult(
        run_id=input.run_id,
        order_id=input.order_id,
        action=action_clean,
        success=True,
        message=msg,
        timestamp=datetime.now(timezone.utc),
    )
