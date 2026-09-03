import asyncio
import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Dict, Any, Optional
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from temporal.activities.persistence import (
        update_run_status_activity,
        update_order_status_activity,
        record_workflow_event_activity,
        update_compact_memory_activity,
        UpdateRunStatusInput,
        UpdateOrderStatusInput,
        RecordWorkflowEventInput,
        UpdateMemoryInput,
    )
    from temporal.activities.agent_activities import (
        execute_agent_decision_activity,
        execute_business_tool_activity,
        ExecuteAgentInput,
        BusinessToolInput,
    )
    from temporal.policies import evaluate_wake_sleep_policy
    from backend.app.models.enums import RunStatus, OrderStatus, ActivityType

EVENT_TO_ORDER_STATUS_MAP = {
    "order_created": OrderStatus.CREATED.value,
    "payment_confirmed": OrderStatus.PAYMENT_CONFIRMED.value,
    "payment_failed": OrderStatus.PAYMENT_FAILED.value,
    "shipment_created": OrderStatus.SHIPMENT_CREATED.value,
    "shipment_delayed": OrderStatus.SHIPMENT_DELAYED.value,
    "delivered": OrderStatus.DELIVERED.value,
    "refund_requested": OrderStatus.REFUND_REQUESTED.value,
}

@dataclass
class OrderSupervisorWorkflowInput:
    run_id: int
    order_id: int
    supervisor_id: int
    order_context: Dict[str, Any] = field(default_factory=dict)
    base_instruction: str = ""
    run_instructions: Optional[str] = None
    initial_order_status: str = "created"
    scheduled_wake_seconds: Optional[float] = None

@dataclass
class OrderEventSignal:
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

@workflow.defn
class OrderSupervisorWorkflow:
    def __init__(self) -> None:
        self.incoming_events: List[OrderEventSignal] = []
        self._termination_requested: bool = False
        self._is_paused: bool = False
        self._is_completed: bool = False
        self._current_status: str = "Initializing"
        self.next_wake_seconds: Optional[float] = None
        self.last_wake_reason: str = "initial"

    @workflow.signal
    def event_signal(self, event: OrderEventSignal) -> None:
        """
        Temporal Signal handler to collect incoming order lifecycle events.
        """
        workflow.logger.info("Signal received: event_type='%s'", event.event_type)
        self.incoming_events.append(event)

    @workflow.signal
    def pause_signal(self) -> None:
        """
        Temporal Signal handler to interrupt/pause workflow execution.
        """
        workflow.logger.info("Signal received: pause_signal")
        self._is_paused = True

    @workflow.signal
    def resume_signal(self) -> None:
        """
        Temporal Signal handler to resume paused workflow execution.
        """
        workflow.logger.info("Signal received: resume_signal")
        self._is_paused = False

    @workflow.signal
    def terminate_signal(self) -> None:
        """
        Temporal Signal handler for manual workflow termination request.
        """
        workflow.logger.info("Signal received: terminate_signal")
        self._termination_requested = True

    @workflow.signal
    def schedule_wake_signal(self, seconds: float) -> None:
        """
        Temporal Signal handler to dynamically set/update a scheduled wake-up timer in seconds.
        """
        workflow.logger.info("Signal received: schedule_wake_signal for %s seconds", seconds)
        if seconds > 0:
            self.next_wake_seconds = seconds

    async def _update_memory_safely(
        self,
        input: OrderSupervisorWorkflowInput,
        retry_policy: RetryPolicy,
        event_type: Optional[str] = None,
        order_status: Optional[str] = None,
        action_taken: Optional[str] = None,
        run_instructions: Optional[str] = None,
        wake_reason: Optional[str] = None,
    ) -> None:
        """
        Safely triggers compact memory update activity via Temporal Activity boundary.
        Any failure during memory update is logged without breaking workflow execution.
        """
        try:
            await workflow.execute_activity(
                update_compact_memory_activity,
                UpdateMemoryInput(
                    run_id=input.run_id,
                    event_type=event_type,
                    order_status=order_status,
                    action_taken=action_taken,
                    run_instructions=run_instructions,
                    wake_reason=wake_reason,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
        except Exception as e:
            workflow.logger.error(
                "Non-fatal memory update failure for Run ID %s: %s",
                input.run_id,
                e,
            )

    @workflow.run
    async def run(self, input: OrderSupervisorWorkflowInput) -> str:
        workflow.logger.info(
            "Starting OrderSupervisorWorkflow for Run ID %s (Order ID %s)",
            input.run_id,
            input.order_id,
        )

        activity_retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
        )

        # 1. Update status to ACTIVE
        self._current_status = "Workflow started - Active supervision"
        await workflow.execute_activity(
            update_run_status_activity,
            UpdateRunStatusInput(
                run_id=input.run_id,
                status=RunStatus.ACTIVE.value,
                current_status=self._current_status,
            ),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=activity_retry_policy,
        )

        # 2. Record initial workflow activation event
        await workflow.execute_activity(
            record_workflow_event_activity,
            RecordWorkflowEventInput(
                run_id=input.run_id,
                type=ActivityType.WAKE_DECISION.value,
                source="temporal_workflow",
                content="Order supervisor workflow initialized and active.",
            ),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=activity_retry_policy,
        )

        # Initialize Compact Memory for the run
        await self._update_memory_safely(
            input,
            activity_retry_policy,
            order_status=input.initial_order_status,
            run_instructions=input.run_instructions,
            wake_reason="Workflow initialized",
        )

        # 3. Initial AI Supervisor Agent Decision & Tool Execution
        await self._run_agent_assessment(input, activity_retry_policy)

        if input.scheduled_wake_seconds and input.scheduled_wake_seconds > 0:
            self.next_wake_seconds = input.scheduled_wake_seconds

        # 4. Main Event Processing Loop (Wake/Sleep/Pause Cycle)
        while not self._termination_requested and not self._is_completed:
            # Handle Interrupt / Pause state
            if self._is_paused:
                self._current_status = "Interrupted - Paused by user request"
                await workflow.execute_activity(
                    update_run_status_activity,
                    UpdateRunStatusInput(
                        run_id=input.run_id,
                        status=RunStatus.INTERRUPTED.value,
                        current_status=self._current_status,
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )
                await workflow.execute_activity(
                    record_workflow_event_activity,
                    RecordWorkflowEventInput(
                        run_id=input.run_id,
                        type=ActivityType.MANUAL_INSTRUCTION.value,
                        source="user_control",
                        content="Supervisor run interrupted/paused by user.",
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )
                await self._update_memory_safely(
                    input,
                    activity_retry_policy,
                    wake_reason="Interrupted by user",
                )

                # Wait until unpaused or terminated
                await workflow.wait_condition(
                    lambda: not self._is_paused or self._termination_requested
                )

                if self._termination_requested:
                    break

                # Workflow Resumed
                self.last_wake_reason = "user_resume"
                self._current_status = "Active - Resumed by user request"
                await workflow.execute_activity(
                    update_run_status_activity,
                    UpdateRunStatusInput(
                        run_id=input.run_id,
                        status=RunStatus.ACTIVE.value,
                        current_status=self._current_status,
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )
                await workflow.execute_activity(
                    record_workflow_event_activity,
                    RecordWorkflowEventInput(
                        run_id=input.run_id,
                        type=ActivityType.MANUAL_INSTRUCTION.value,
                        source="user_control",
                        content="Supervisor run resumed by user.",
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )
                await self._update_memory_safely(
                    input,
                    activity_retry_policy,
                    wake_reason="Resumed by user",
                )

            # Check if workflow should enter SLEEP state
            if not self.incoming_events and not self._is_paused:
                self._current_status = (
                    f"Asleep - Waiting for events (scheduled wake in {self.next_wake_seconds}s)"
                    if self.next_wake_seconds
                    else "Asleep - Waiting for event signal"
                )
                await workflow.execute_activity(
                    update_run_status_activity,
                    UpdateRunStatusInput(
                        run_id=input.run_id,
                        status=RunStatus.ASLEEP.value,
                        current_status=self._current_status,
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )

                woke_by_timer = False
                try:
                    timeout_duration = (
                        timedelta(seconds=self.next_wake_seconds)
                        if self.next_wake_seconds
                        else None
                    )

                    if timeout_duration:
                        await workflow.wait_condition(
                            lambda: len(self.incoming_events) > 0 or self._is_paused or self._termination_requested,
                            timeout=timeout_duration,
                        )
                    else:
                        await workflow.wait_condition(
                            lambda: len(self.incoming_events) > 0 or self._is_paused or self._termination_requested
                        )
                except asyncio.TimeoutError:
                    woke_by_timer = True

                if woke_by_timer:
                    self.last_wake_reason = "scheduled_timer"
                    workflow.logger.info("Scheduled Temporal timer expired. Waking workflow.")
                    self.next_wake_seconds = None  # Consume timer

                    await workflow.execute_activity(
                        record_workflow_event_activity,
                        RecordWorkflowEventInput(
                            run_id=input.run_id,
                            type=ActivityType.WAKE_DECISION.value,
                            source="scheduled_timer",
                            content="Workflow woke up due to scheduled Temporal timer expiration.",
                        ),
                        start_to_close_timeout=timedelta(seconds=10),
                        retry_policy=activity_retry_policy,
                    )

            if self._termination_requested:
                break

            if self._is_paused:
                continue

            # Wake up and switch back to ACTIVE
            self.last_wake_reason = "signal" if self.incoming_events else self.last_wake_reason
            self._current_status = f"Active - Processing (wake reason: {self.last_wake_reason})"
            await workflow.execute_activity(
                update_run_status_activity,
                UpdateRunStatusInput(
                    run_id=input.run_id,
                    status=RunStatus.ACTIVE.value,
                    current_status=self._current_status,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=activity_retry_policy,
            )

            # Process queued events safely outside signal handler
            while self.incoming_events and not self._is_paused:
                event = self.incoming_events.pop(0)
                workflow.logger.info("Processing event: %s", event.event_type)

                # Evaluate Wake/Sleep Policy
                policy_decision = evaluate_wake_sleep_policy(event.event_type)
                workflow.logger.info(
                    "Wake/Sleep Policy for event '%s': decision='%s', priority='%s'",
                    event.event_type,
                    policy_decision.decision,
                    policy_decision.priority,
                )

                # Record Wake/Sleep Policy decision via Activity
                await workflow.execute_activity(
                    record_workflow_event_activity,
                    RecordWorkflowEventInput(
                        run_id=input.run_id,
                        type=ActivityType.WAKE_DECISION.value,
                        source="wake_sleep_policy",
                        content=f"Policy decision '{policy_decision.decision.upper()}' for event '{event.event_type}': {policy_decision.reason}",
                        activity_metadata={
                            "decision": policy_decision.decision,
                            "reason": policy_decision.reason,
                            "priority": policy_decision.priority,
                            "event_type": event.event_type,
                        },
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )

                # Update order status in database if event matches a lifecycle transition
                mapped_order_status = EVENT_TO_ORDER_STATUS_MAP.get(event.event_type)
                if mapped_order_status:
                    await workflow.execute_activity(
                        update_order_status_activity,
                        UpdateOrderStatusInput(
                            order_id=input.order_id,
                            status=mapped_order_status,
                        ),
                        start_to_close_timeout=timedelta(seconds=10),
                        retry_policy=activity_retry_policy,
                    )

                # Log incoming event via Activity
                await workflow.execute_activity(
                    record_workflow_event_activity,
                    RecordWorkflowEventInput(
                        run_id=input.run_id,
                        type=ActivityType.INCOMING_EVENT.value,
                        source="event_signal",
                        content=f"Received order event: {event.event_type}",
                        activity_metadata={
                            "event_type": event.event_type,
                            "payload": event.payload,
                            "timestamp": event.timestamp,
                        },
                    ),
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=activity_retry_policy,
                )

                # Update compact memory for event
                await self._update_memory_safely(
                    input,
                    activity_retry_policy,
                    event_type=event.event_type,
                    order_status=mapped_order_status,
                    wake_reason=f"Woken by {event.event_type} signal",
                )

                # Trigger AI Agent & Tool Execution if policy decision is WAKE
                if policy_decision.decision == "wake":
                    await self._run_agent_assessment(input, activity_retry_policy, event=event)

                # Lifecycle terminal state check
                if event.event_type == "delivered":
                    workflow.logger.info("Terminal event 'delivered' received. Completing workflow.")
                    self._is_completed = True
                    break

        # 5. Workflow Exit Handling
        if self._termination_requested:
            self._current_status = "Terminated by user request"
            await workflow.execute_activity(
                update_run_status_activity,
                UpdateRunStatusInput(
                    run_id=input.run_id,
                    status=RunStatus.TERMINATED.value,
                    current_status=self._current_status,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=activity_retry_policy,
            )
            await workflow.execute_activity(
                record_workflow_event_activity,
                RecordWorkflowEventInput(
                    run_id=input.run_id,
                    type=ActivityType.MANUAL_INSTRUCTION.value,
                    source="user_control",
                    content="Supervisor run terminated by user request.",
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=activity_retry_policy,
            )
            await self._update_memory_safely(
                input,
                activity_retry_policy,
                wake_reason="Terminated by user",
            )
            return f"Workflow terminated for Order ID {input.order_id}"

        # Terminal Completion State
        self._current_status = "Completed - Order lifecycle finished"
        await workflow.execute_activity(
            update_run_status_activity,
            UpdateRunStatusInput(
                run_id=input.run_id,
                status=RunStatus.COMPLETED.value,
                current_status=self._current_status,
            ),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=activity_retry_policy,
        )
        await workflow.execute_activity(
            record_workflow_event_activity,
            RecordWorkflowEventInput(
                run_id=input.run_id,
                type=ActivityType.FINAL_OUTPUT.value,
                source="temporal_workflow",
                content="Order lifecycle completed successfully.",
            ),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=activity_retry_policy,
        )
        return f"Workflow completed successfully for Order ID {input.order_id}"

    async def _run_agent_assessment(
        self,
        input: OrderSupervisorWorkflowInput,
        retry_policy: RetryPolicy,
        event: Optional[OrderEventSignal] = None,
    ) -> None:
        """
        Executes AI Supervisor Agent decision activity & simulated business tool activity.
        All non-deterministic LLM reasoning and tool execution happen through Temporal Activities.
        """
        if self._is_paused:
            workflow.logger.info("Workflow is paused; skipping AI Supervisor Agent assessment.")
            return

        event_type = event.event_type if event else "order_created"
        event_payload = event.payload if event else {}

        workflow.logger.info("Executing AI Supervisor Agent decision activity for event '%s'", event_type)
        agent_decision = await workflow.execute_activity(
            execute_agent_decision_activity,
            ExecuteAgentInput(
                run_id=input.run_id,
                order_id=input.order_id,
                event_type=event_type,
                event_payload=event_payload,
            ),
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        if agent_decision:
            if isinstance(agent_decision, dict):
                action_name = agent_decision.get("action")
                reasoning_msg = agent_decision.get("reasoning", "")
                action_payload = agent_decision.get("action_payload", {})
                needs_future_wake = agent_decision.get("needs_future_wake")
                recommended_wake_seconds = agent_decision.get("recommended_wake_seconds")
            else:
                action_name = getattr(agent_decision, "action", "no_action")
                reasoning_msg = getattr(agent_decision, "reasoning", "")
                action_payload = getattr(agent_decision, "action_payload", {})
                needs_future_wake = getattr(agent_decision, "needs_future_wake", False)
                recommended_wake_seconds = getattr(agent_decision, "recommended_wake_seconds", None)

            if action_name and action_name != "no_action":
                workflow.logger.info("Executing simulated business tool activity '%s'", action_name)
                await workflow.execute_activity(
                    execute_business_tool_activity,
                    BusinessToolInput(
                        run_id=input.run_id,
                        order_id=input.order_id,
                        action=action_name,
                        action_payload=action_payload,
                        reasoning=reasoning_msg,
                    ),
                    start_to_close_timeout=timedelta(seconds=15),
                    retry_policy=retry_policy,
                )

                # Update memory with action taken
                await self._update_memory_safely(
                    input,
                    retry_policy,
                    action_taken=action_name,
                )

            # Schedule future wake-up timer if agent recommended it
            if needs_future_wake and recommended_wake_seconds and recommended_wake_seconds > 0:
                workflow.logger.info("AI Agent recommended scheduled wake-up in %s seconds", recommended_wake_seconds)
                self.next_wake_seconds = recommended_wake_seconds
