from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_BUSINESS_TOOLS = [
    "message_fulfillment_team",
    "message_payments_team",
    "message_logistics_team",
    "message_customer",
    "create_internal_note",
]

class AgentContextInput(BaseModel):
    run_id: int
    order_id: int
    event_type: str
    event_payload: Dict[str, Any] = Field(default_factory=dict)
    current_order_status: str = ""
    supervisor_name: str = ""
    base_instruction: str = ""
    run_instructions: Optional[str] = None
    compact_memory_summary: str = ""
    available_tools: List[str] = Field(default_factory=list)
    recent_timeline: List[Dict[str, Any]] = Field(default_factory=list)

class AgentDecision(BaseModel):
    action: str  # Must be one of ALLOWED_BUSINESS_TOOLS or "no_action"
    reasoning: str
    action_payload: Dict[str, Any] = Field(default_factory=dict)
    needs_future_wake: bool = False
    recommended_wake_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        v_clean = v.strip().lower() if v else "no_action"
        if v_clean != "no_action" and v_clean not in ALLOWED_BUSINESS_TOOLS:
            raise ValueError(
                f"Invalid action '{v}'. Allowed actions: {ALLOWED_BUSINESS_TOOLS} or 'no_action'"
            )
        return v_clean

class ToolExecutionResult(BaseModel):
    run_id: int
    order_id: int
    action: str
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
