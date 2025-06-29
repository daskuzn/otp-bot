"""Base mixin & declarative base import shortcut."""
from datetime import datetime as dt
import datetime

from sqlalchemy import Column, DateTime

from database.db import Base

class TimestampMixin:
    created_at = Column(DateTime, default=dt.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=dt.now(datetime.timezone.utc),
        onupdate=dt.now(datetime.timezone.utc),
        nullable=False,
    )

# Re‑export Base so other modules can import from bot.models.base
__all__ = ["Base", "TimestampMixin"]