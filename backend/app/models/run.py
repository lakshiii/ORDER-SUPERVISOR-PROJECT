from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base
from backend.app.models.enums import RunStatus

if TYPE_CHECKING:
    from backend.app.models.order import Order
    from backend.app.models.supervisor import Supervisor
    from backend.app.models.activity import Activity
    from backend.app.models.memory import Memory
    from backend.app.models.final_summary import FinalSummary

class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    supervisor_id: Mapped[int | None] = mapped_column(ForeignKey("supervisors.id", ondelete="SET NULL"), nullable=True, index=True)
    temporal_workflow_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    status: Mapped[str] = mapped_column(String(50), default=RunStatus.PENDING.value, nullable=False)
    run_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_status: Mapped[str] = mapped_column(String(255), default="Initialized", nullable=False)
    sleep_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="runs")
    supervisor: Mapped["Supervisor | None"] = relationship("Supervisor", back_populates="runs")
    activities: Mapped[List["Activity"]] = relationship("Activity", back_populates="run", cascade="all, delete-orphan")
    memory: Mapped["Memory | None"] = relationship("Memory", back_populates="run", uselist=False, cascade="all, delete-orphan")
    final_summary: Mapped["FinalSummary | None"] = relationship("FinalSummary", back_populates="run", uselist=False, cascade="all, delete-orphan")
