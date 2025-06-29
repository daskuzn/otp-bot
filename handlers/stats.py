from aiogram import Router, F
from aiogram.types import CallbackQuery
from babel.dates import format_date
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Visit

router = Router()

@router.callback_query(F.data == "stats")
async def command_stats(callback: CallbackQuery, session: AsyncSession):
    # 1. начало текущего месяца (время в msg.date уже UTC с tzinfo)
    month_start = callback.message.date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 2. считаем визиты: JOIN users → visits по user.id = visit.rep_id
    visits_q = (
        select(func.count())
        .select_from(Visit)
        .join(User, User.id == Visit.rep_id)
        .where(
            User.telegram_id == callback.from_user.id,   # ← фильтр по telegram_id
            Visit.visited_at >= month_start,
        )
    )

    visits_cnt: int = await session.scalar(visits_q)

    # 3. аккуратное название месяца на русском
    month_name_ru = format_date(callback.message.date, "LLLL", locale="ru").capitalize()

    text = (
        f"Отчёт за {month_name_ru}:\n"
        f"• Визитов: {visits_cnt}"
    )
    await callback.message.answer(text)
