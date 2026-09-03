from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict

class FinalSummaryBase(BaseModel):
    summary: str
    important_actions: List[str] = []
    key_learnings: List[str] = []
    recommendations: List[str] = []

class FinalSummaryCreate(FinalSummaryBase):
    run_id: int

class FinalSummaryResponse(FinalSummaryBase):
    id: int
    run_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
