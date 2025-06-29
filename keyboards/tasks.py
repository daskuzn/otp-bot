from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from models import User, UserRole

def admin_tasks_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Новая задача", callback_data="task_new")
    kb.button(text="🗑 Скрыть сообщение", callback_data="delete")
    kb.adjust(1)
    return kb.as_markup()


def partners_kb(partners):
    kb = InlineKeyboardBuilder()
    for p in partners:
        kb.button(text=p.name, callback_data=f"tp_partner_{p.id}")
    kb.adjust(2)                       # две кнопки в ряд
    return kb.as_markup()


def task_types_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Обучение", callback_data="tp_type_TRAINING")
    kb.button(text="Визит", callback_data="tp_type_VISIT")
    kb.button(text="Доставка", callback_data="tp_type_DELIVERY")
    kb.button(text="Обратная связь", callback_data="tp_type_FEEDBACK")
    kb.adjust(1)
    return kb.as_markup()


def confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Сохранить", callback_data="tp_ok")
    kb.button(text="↩️ Отмена",    callback_data="tp_cancel")
    kb.adjust(2)
    return kb.as_markup()


async def reps_kb(session):
    reps = (await session.execute(
        select(User).where(User.role == UserRole.REP)
    )).scalars().all()
    r: User
    kb = InlineKeyboardBuilder()
    for r in reps:
        kb.button(
            text=f"{r.last_name} {r.first_name}",
            callback_data=f"tp_rep_{r.id}"
        )
    kb.adjust(1)        # по два в строке
    return kb.as_markup()