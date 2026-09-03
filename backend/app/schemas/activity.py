from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.enums import ActivityType

class ActivityBase(BaseModel):
    type: ActivityType
    source: str = "system"
    content: str
    activity_metadata: Optional[Dict[str, Any]] = None

class ActivityCreate(ActivityBase):
    run_id: int

class ActivityResponse(ActivityBase):
    id: int
    run_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
