import os
import logging
from typing import Optional
from dotenv import load_dotenv
from temporalio.client import Client
from temporal.workflows.order_supervisor import (
    OrderSupervisorWorkflow,
    OrderSupervisorWorkflowInput,
    OrderEventSignal,
)

load_dotenv()

logger = logging.getLogger("temporal_client")

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = "order-supervisor"

async def get_temporal_client() -> Client:
    """
    Connects to the Temporal server using environment configuration.
    """
    logger.info("Connecting to Temporal server at %s (namespace: %s)...", TEMPORAL_HOST, TEMPORAL_NAMESPACE)
    client = await Client.connect(
        target_host=TEMPORAL_HOST,
        namespace=TEMPORAL_NAMESPACE,
    )
    return client

async def start_order_supervisor_workflow(input: OrderSupervisorWorkflowInput) -> str:
    """
    Starts an OrderSupervisorWorkflow for an order run.
    Uses deterministic Workflow ID: order-supervisor-{order_id}
    """
    workflow_id = f"order-supervisor-{input.order_id}"
    client = await get_temporal_client()

    logger.info("Dispatching OrderSupervisorWorkflow with ID '%s' on task queue '%s'", workflow_id, TASK_QUEUE)
    handle = await client.start_workflow(
        OrderSupervisorWorkflow.run,
        input,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )
    return handle.id

async def send_event_signal_to_workflow(workflow_id: str, event: OrderEventSignal) -> None:
    """
    Sends an event_signal to a running OrderSupervisorWorkflow.
    """
    client = await get_temporal_client()
    logger.info("Sending event_signal '%s' to Workflow ID '%s'", event.event_type, workflow_id)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(OrderSupervisorWorkflow.event_signal, event)

async def send_pause_signal_to_workflow(workflow_id: str) -> None:
    """
    Sends a pause_signal to an OrderSupervisorWorkflow.
    """
    client = await get_temporal_client()
    logger.info("Sending pause_signal to Workflow ID '%s'", workflow_id)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(OrderSupervisorWorkflow.pause_signal)

async def send_resume_signal_to_workflow(workflow_id: str) -> None:
    """
    Sends a resume_signal to an OrderSupervisorWorkflow.
    """
    client = await get_temporal_client()
    logger.info("Sending resume_signal to Workflow ID '%s'", workflow_id)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(OrderSupervisorWorkflow.resume_signal)

async def send_terminate_signal_to_workflow(workflow_id: str) -> None:
    """
    Sends a terminate_signal to an OrderSupervisorWorkflow.
    """
    client = await get_temporal_client()
    logger.info("Sending terminate_signal to Workflow ID '%s'", workflow_id)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(OrderSupervisorWorkflow.terminate_signal)
