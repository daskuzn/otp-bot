from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import Row, Sequence, Tuple, select

from database.db import async_session_factory
from models import Task, Partner, User, Visit, Report
from models.enums import TaskStatus

# Yes / partial / no for marketing materials

async def get_tasks_kb():
    kb = InlineKeyboardBuilder()
    stmt = (
        select(Task, Partner)
        .join(Partner, Task.partner_id == Partner.id)
        .where(Task.status == TaskStatus.PENDING)
    )
    async with async_session_factory() as session:
        rows = (await session.execute(stmt)).all()
    task: Task
    partner: Partner
    for task, partner in rows:
        btn_text = f"{task.task_type}. Партнер: {partner.name}"
        kb.button(text=btn_text, callback_data=f"task_{task.id}")
        
    kb.adjust(1)
    return kb.as_markup()


def marketing_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data="mkt_yes")
    kb.button(text="⚠️ Частично", callback_data="mkt_partial")
    kb.button(text="❌ Нет", callback_data="mkt_no")
    kb.adjust(1)
    return kb.as_markup()


def continue_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data="continue_yes", cache_time=3)
    kb.button(text="❌ Нет", callback_data="continue_no", cache_time=3)
    kb.adjust(1)
    return kb.as_markup()


async def admin_reports_kb(reports_list: list[Report]) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for report in reports_list:
        btn_text = f"ID отчёта: {report.id}"
        kb.button(text=btn_text, callback_data=f"report_{report.id}")

    kb.button(text="Скрыть сообщение", callback_data="delete")
    kb.adjust(1)
    return kb.as_markup()


def delete_msg_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="Скрыть сообщение", callback_data="delete")
    kb.adjust(1)
    return kb.as_markup()


def confirm_report_kb(visit_id: int) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data=f"confirm_yes:{visit_id}")
    kb.button(text="❌ Нет", callback_data=f"confirm_no:{visit_id}")
    kb.button(text="Скрыть сообщение", callback_data="delete")
    kb.adjust(1)
    return kb.as_markup()