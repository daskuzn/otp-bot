"""Application‑level enums mapped to existing PostgreSQL enum types."""
from enum import StrEnum

class UserRole(StrEnum):
    ADMIN = "ADMIN"
    REP = "REP"

class TaskType(StrEnum):
    CALL = "CALL"
    VISIT = "VISIT"
    DELIVERY = "DELIVERY"

class TaskStatus(StrEnum):
    PENDING = "PENDING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"