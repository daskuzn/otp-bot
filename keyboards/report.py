from aiogram.utils.keyboard import InlineKeyboardBuilder

# Yes / partial / no for marketing materials

def marketing_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data="mkt_yes")
    kb.button(text="⚠️ Частично", callback_data="mkt_partial")
    kb.button(text="❌ Нет", callback_data="mkt_no")
    kb.adjust(1)
    return kb.as_markup()

# competitors multi‑select will be built dynamically