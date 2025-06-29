from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from common.ctx import current_session

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, factory: async_sessionmaker[AsyncSession]):
        self.factory = factory

    async def __call__(self, handler, event, data):
        async with self.factory() as session:
            data["session"] = session      # будет доступно как параметр `session`
            return await handler(event, data)
        