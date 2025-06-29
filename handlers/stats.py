from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.visit import Visit
from models.partner import Partner
from models.competitor_offer import CompetitorOffer

router = Router()

@router.message(Command("stats"))
async def command_stats(message: Message, session: AsyncSession):
    # Простейший пример статистики по текущему месяцу
    month_start = message.date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    visits_q = select(func.count()).where(Visit.rep_id == message.from_user.id, Visit.visited_at >= month_start)
    visits_cnt = (await session.execute(visits_q)).scalar_one()
    text = f"Отчёт за {message.date:%B}:\n• Визитов: {visits_cnt}"
    await message.answer(text)