from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

if TYPE_CHECKING:
    from backend.app.models.run import Run

class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    current_status: Mapped[str] = mapped_column(String(255), nullable=False, default="Initialized")
    next_wake_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="memory")
