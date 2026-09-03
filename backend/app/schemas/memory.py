from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MemoryBase(BaseModel):
    summary: str
    current_status: str
    next_wake_at: Optional[datetime] = None

class MemoryCreate(MemoryBase):
    run_id: int

class MemoryResponse(MemoryBase):
    id: int
    run_id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
