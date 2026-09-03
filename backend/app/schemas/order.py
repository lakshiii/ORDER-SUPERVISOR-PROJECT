from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from backend.app.schemas.enums import OrderStatus

class OrderBase(BaseModel):
    external_order_id: str
    customer_name: Optional[str] = None
    status: OrderStatus = OrderStatus.CREATED

    @field_validator("external_order_id")
    @classmethod
    def validate_external_order_id(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("external_order_id cannot be empty")
        return v_stripped

class OrderCreate(BaseModel):
    external_order_id: str
    customer_name: Optional[str] = None

    @field_validator("external_order_id")
    @classmethod
    def validate_external_order_id(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("external_order_id cannot be empty")
        return v_stripped

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
