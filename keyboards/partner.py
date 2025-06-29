# ───────── keyboards/partners.py ─────────
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_partners_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить партнёра", callback_data="add_partner")
    kb.button(text="🗑 Скрыть сообщение", callback_data="delete")
    kb.adjust(1)
    return kb.as_markup()
