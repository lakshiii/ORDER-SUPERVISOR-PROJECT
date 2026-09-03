from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator

SUPPORTED_EVENT_TYPES = {
    "order_created",
    "payment_confirmed",
    "payment_failed",
    "shipment_created",
    "shipment_delayed",
    "delivered",
    "refund_requested",
    "customer_message_received",
    "no_update_for_n_hours",
}

class EventCreate(BaseModel):
    event_type: str
    payload: Dict[str, Any] = {}
    source: str = "simulator"

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in SUPPORTED_EVENT_TYPES:
            raise ValueError(
                f"Unsupported event_type '{v}'. Allowed types: {sorted(list(SUPPORTED_EVENT_TYPES))}"
            )
        return v_clean

class EventResponse(BaseModel):
    run_id: int
    workflow_id: str
    event_type: str
    status: str = "accepted"
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
