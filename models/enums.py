"""Application‑level enums mapped to existing PostgreSQL enum types."""
from enum import StrEnum

class UserRole(StrEnum):
    ADMIN = "ADMIN"
    REP = "REP"

class TaskType(StrEnum):
    TRAINING = "TRAINING"
    VISIT = "VISIT"
    FEEDBACK = "FEEDBACK"
    DELIVERY = "DELIVERY"

class TaskStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELED = "CANCELED"

class Marketing(StrEnum):
    YES = "yes"
    PARTIAL = "partial"
    NO = "no"
