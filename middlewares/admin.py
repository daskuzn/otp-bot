from aiogram.types import Message, CallbackQuery

from sqlalchemy import select

from typing import Callable, Awaitable, Dict, Any

from database.db import async_session_factory
from models import User, UserRole

class AdminMiddleware:
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Awaitable[Any] | None:
        if isinstance(message, CallbackQuery):
            temp_msg = await message.message.answer("Проверка прав администратора...")
        else:
            temp_msg = await message.answer("Проверка прав администратора...")
        user_id = message.from_user.id

        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalars().first()

            if user.role == UserRole.ADMIN:
                await temp_msg.delete()
                return await handler(message, data)
            else:
                await message.answer("Доступ запрещен. Вы не являетесь администратором")
                return None
            