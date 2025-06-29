# """Attach a database session to every handler call."""
# from typing import Any, Awaitable, Callable, Dict

# from aiogram import BaseMiddleware
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# class DBSessionMiddleware(BaseMiddleware):
#     def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
#         self._session_factory = session_factory

#     async def __call__(
#         self,
#         handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
#         event: Any,
#         data: Dict[str, Any],
#     ) -> Any:
#         async with self._session_factory() as session:
#             data["session"] = session  # make session injectable into handlers
#             result = await handler(event, data)
#             # Commit if no exceptions were raised inside handler
#             await session.commit()
#             return result
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from common.ctx import current_session

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, factory: async_sessionmaker[AsyncSession]):
        self.factory = factory

    async def __call__(self, handler, event, data):
        async with self.factory() as session:
            token = current_session.set(session)
            try:
                return await handler(event, data)
            finally:
                current_session.reset(token)
