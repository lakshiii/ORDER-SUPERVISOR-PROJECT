from enum import Enum

class RunStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SLEEPING = "sleeping"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    TERMINATED = "terminated"

class OrderStatus(str, Enum):
    CREATED = "created"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    SHIPMENT_CREATED = "shipment_created"
    SHIPMENT_DELAYED = "shipment_delayed"
    DELIVERED = "delivered"
    REFUND_REQUESTED = "refund_requested"

class ActivityType(str, Enum):
    INCOMING_EVENT = "incoming_event"
    WAKE_DECISION = "wake_decision"
    SLEEP_DECISION = "sleep_decision"
    AGENT_ACTION = "agent_action"
    MANUAL_INSTRUCTION = "manual_instruction"
    FINAL_OUTPUT = "final_output"
