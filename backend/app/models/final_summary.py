from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

if TYPE_CHECKING:
    from backend.app.models.run import Run

class FinalSummary(Base):
    __tablename__ = "final_summaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    important_actions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    key_learnings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="final_summary")
