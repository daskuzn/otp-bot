import asyncio
import logging

from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from middlewares.db import DBSessionMiddleware
from middlewares.user import CurrentUserMiddleware
from database.db import async_session_factory, engine
from models import Base
from handlers.admin import router as admin_router
from handlers.start import router as start_router
from handlers.report import router as report_router
from handlers.menu import router as menu_router


# logging.basicConfig(level=logging.INFO)
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# async def main():
#     bot = Bot(token=BOT_TOKEN,
#               default=DefaultBotProperties(parse_mode=ParseMode.HTML))
#     dp = Dispatcher()

#     dp.include_router(start_router)
#     dp.include_router(menu_router)
#     dp.include_router(report_router)
#     dp.include_router(admin_router)

#     dp.message.outer_middleware(DBSessionMiddleware(async_session_factory))
#     dp.callback_query.outer_middleware(DBSessionMiddleware(async_session_factory))

#     dp.message.outer_middleware(CurrentUserMiddleware())      # 👈 теперь тоже outer
#     dp.callback_query.outer_middleware(CurrentUserMiddleware())

#     await on_startup()
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())

from middlewares.db import DBSessionMiddleware
from database.db import async_session_factory
# (другие импорты)
from handlers.menu import router as menu_router


async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # 👉 1. Сначала подключаем OUTER-middleware сессии БД
    dp.message.outer_middleware(DBSessionMiddleware(async_session_factory))
    dp.callback_query.outer_middleware(DBSessionMiddleware(async_session_factory))

    # (если используете CurrentUserMiddleware, добавьте его СРАЗУ после БД-middleware)
    # dp.message.outer_middleware(CurrentUserMiddleware())
    # dp.callback_query.outer_middleware(CurrentUserMiddleware())

    # 👉 2. Затем регистрируем все роутеры
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(report_router)
    dp.include_router(admin_router)

    # 👉 3. Запускаем бота
    await on_startup()
    await dp.start_polling(bot)