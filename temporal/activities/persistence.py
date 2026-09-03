import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from temporalio import activity
import backend.app.database as db_module
from backend.app.models.run import Run
from backend.app.models.order import Order
from backend.app.models.activity import Activity
from backend.app.models.enums import RunStatus
from backend.app.services.memory_service import update_compact_memory

logger = logging.getLogger("persistence_activities")

@dataclass
class UpdateRunStatusInput:
    run_id: int
    status: str
    current_status: Optional[str] = None

@dataclass
class UpdateOrderStatusInput:
    order_id: int
    status: str

@dataclass
class RecordWorkflowEventInput:
    run_id: int
    type: str
    source: str
    content: str
    activity_metadata: Optional[Dict[str, Any]] = None

@dataclass
class UpdateMemoryInput:
    run_id: int
    event_type: Optional[str] = None
    order_status: Optional[str] = None
    action_taken: Optional[str] = None
    run_instructions: Optional[str] = None
    wake_reason: Optional[str] = None
    next_wake_at: Optional[str] = None

def save_activity_event(
    run_id: int,
    type_str: str,
    source: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None,
) -> int:
    """
    Internal helper to record activity events directly in database session.
    Reuses provided session if available to prevent SQLite transaction locking.
    """
    close_db_on_exit = False
    if db is None:
        db = db_module.SessionLocal()
        close_db_on_exit = True
    try:
        activity_record = Activity(
            run_id=run_id,
            type=type_str,
            source=source,
            content=content,
            activity_metadata=metadata,
        )
        db.add(activity_record)
        db.commit()
        db.refresh(activity_record)
        return activity_record.id
    except Exception as e:
        db.rollback()
        logger.error("Error in save_activity_event: %s", e)
        raise e
    finally:
        if close_db_on_exit:
            db.close()

@activity.defn
async def update_run_status_activity(input: UpdateRunStatusInput) -> bool:
    """
    Temporal Activity to update Run status and current_status in database.
    """
    logger.info("Activity update_run_status")
    db = db_module.SessionLocal()
    try:
        run_id = input.get("run_id") if isinstance(input, dict) else getattr(input, "run_id")
        status = input.get("status") if isinstance(input, dict) else getattr(input, "status")
        current_status = input.get("current_status") if isinstance(input, dict) else getattr(input, "current_status", None)

        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            logger.error("Activity update_run_status failed: Run ID %s not found", run_id)
            return False

        run.status = status
        if current_status:
            run.current_status = current_status

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error("Error in update_run_status_activity: %s", e)
        raise e
    finally:
        db.close()

@activity.defn
async def update_order_status_activity(input: UpdateOrderStatusInput) -> bool:
    """
    Temporal Activity to update Order status in database.
    """
    logger.info("Activity update_order_status")
    db = db_module.SessionLocal()
    try:
        order_id = input.get("order_id") if isinstance(input, dict) else getattr(input, "order_id")
        status = input.get("status") if isinstance(input, dict) else getattr(input, "status")

        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error("Activity update_order_status failed: Order ID %s not found", order_id)
            return False

        order.status = status
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error("Error in update_order_status_activity: %s", e)
        raise e
    finally:
        db.close()

@activity.defn
async def record_workflow_event_activity(input: RecordWorkflowEventInput) -> int:
    """
    Temporal Activity to log a timeline entry into the activities table in database.
    """
    if isinstance(input, dict):
        run_id = input.get("run_id")
        type_str = input.get("type")
        source = input.get("source")
        content = input.get("content")
        metadata = input.get("activity_metadata")
    else:
        run_id = getattr(input, "run_id")
        type_str = getattr(input, "type")
        source = getattr(input, "source")
        content = getattr(input, "content")
        metadata = getattr(input, "activity_metadata", None)

    logger.info(
        "Activity record_workflow_event: Run ID %s, type='%s', source='%s', content='%s'",
        run_id,
        type_str,
        source,
        content,
    )
    return save_activity_event(
        run_id=run_id,
        type_str=type_str,
        source=source,
        content=content,
        metadata=metadata,
    )

@activity.defn
async def update_compact_memory_activity(input: UpdateMemoryInput) -> str:
    """
    Temporal Activity boundary for updating run-level compact working memory.
    Safely parses dict or dataclass payload inputs.
    """
    if isinstance(input, dict):
        run_id = input.get("run_id")
        event_type = input.get("event_type")
        order_status = input.get("order_status")
        action_taken = input.get("action_taken")
        run_instructions = input.get("run_instructions")
        wake_reason = input.get("wake_reason")
    else:
        run_id = getattr(input, "run_id")
        event_type = getattr(input, "event_type", None)
        order_status = getattr(input, "order_status", None)
        action_taken = getattr(input, "action_taken", None)
        run_instructions = getattr(input, "run_instructions", None)
        wake_reason = getattr(input, "wake_reason", None)

    logger.info("Activity update_compact_memory: Run ID %s", run_id)
    db = db_module.SessionLocal()
    try:
        memory = update_compact_memory(
            db=db,
            run_id=run_id,
            event_type=event_type,
            order_status=order_status,
            action_taken=action_taken,
            run_instructions=run_instructions,
            wake_reason=wake_reason,
        )
        return memory.summary
    except Exception as e:
        db.rollback()
        logger.error("Error in update_compact_memory_activity for Run ID %s: %s", run_id, e)
        raise e
    finally:
        db.close()
