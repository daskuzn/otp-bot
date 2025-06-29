from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession

current_session: ContextVar[AsyncSession | None] = ContextVar(
    "current_session",
    default=None,
)
