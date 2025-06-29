from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import TimestampMixin, Base
from ._types import pg_enum
from .enums import TaskType, TaskStatus

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    rep_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)

    task_type = Column(pg_enum(TaskType, "tasktype"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(pg_enum(TaskStatus, "taskstatus"), nullable=False, server_default=TaskStatus.PENDING.value)
    details = Column(Text, nullable=True)

    # TimestampMixin already provides created_at/updated_at

    rep = relationship("User", back_populates="tasks")
    partner = relationship("Partner", back_populates="tasks")
    report = relationship(
        "Report",
        back_populates="task",
        uselist=False,          # ← один Report
        cascade="all, delete-orphan",  # опционально
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Task id={self.id} rep={self.rep_id} partner={self.partner_id}>"
    