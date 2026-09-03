from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

if TYPE_CHECKING:
    from backend.app.models.run import Run

class Supervisor(Base):
    __tablename__ = "supervisors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_instruction: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), default="gemini-2.5-flash", nullable=False)
    aggressiveness: Mapped[str] = mapped_column(String(50), default="normal", nullable=False)
    default_wake_up: Mapped[str | None] = mapped_column(String(255), nullable=True)
    available_tools: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    runs: Mapped[List["Run"]] = relationship("Run", back_populates="supervisor")
