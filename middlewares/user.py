"""Load current user from DB and inject into handler data."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

class CurrentUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        from_user = event.from_user  # Message | CallbackQuery
        if not from_user:
            return await handler(event, data)
        stmt = select(User).where(User.telegram_id == from_user.id)
        user = await session.scalar(stmt)
        data["current_user"] = user
        return await handler(event, data)