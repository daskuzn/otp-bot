import asyncio
import logging

from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from middlewares.db import DBSessionMiddleware
from database.db import async_session_factory
from handlers.admin import router as admin_router
from handlers.start import router as start_router
from handlers.report import router as report_router
from handlers.stats import router as stats_router


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.message.middleware(DBSessionMiddleware(async_session_factory))
dp.callback_query.middleware(DBSessionMiddleware(async_session_factory))

dp.include_routers(
        admin_router,
        start_router,
        report_router,
        stats_router,
    )

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())