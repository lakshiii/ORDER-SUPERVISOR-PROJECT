import asyncio
import logging
import os
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from temporal.workflows.order_supervisor import OrderSupervisorWorkflow
from temporal.activities.persistence import (
    update_run_status_activity,
    update_order_status_activity,
    record_workflow_event_activity,
    update_compact_memory_activity,
)
from temporal.activities.agent_activities import (
    execute_agent_decision_activity,
    execute_business_tool_activity,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("temporal_worker")

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = "order-supervisor"

async def main():
    logger.info("Connecting Temporal worker to %s (namespace: %s)...", TEMPORAL_HOST, TEMPORAL_NAMESPACE)
    client = await Client.connect(
        target_host=TEMPORAL_HOST,
        namespace=TEMPORAL_NAMESPACE,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OrderSupervisorWorkflow],
        activities=[
            update_run_status_activity,
            update_order_status_activity,
            record_workflow_event_activity,
            update_compact_memory_activity,
            execute_agent_decision_activity,
            execute_business_tool_activity,
        ],
    )

    logger.info("Temporal Worker listening on task queue '%s'. Press Ctrl+C to exit.", TASK_QUEUE)
    await worker.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Temporal Worker stopped.")
