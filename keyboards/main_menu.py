from aiogram.utils.keyboard import InlineKeyboardBuilder

REP_BUTTONS = [
    ("📍 Отправить отчёт о визите", "start_report"),
    ("📊 Моя статистика",          "stats")
]

ADMIN_BUTTONS = [
    ("👤 Представители",           "admin_reps"),
    ("👥 Партнёры",                "admin_partners"),
    ("📅 Задачи",                  "admin_tasks"),
    ("🧾 Отчёты",                  "admin_reports"),
    ("📊 Аналитика",               "admin_analytics"),
]

def main_menu(is_admin: bool):
    kb = InlineKeyboardBuilder()
    for text, cb in (ADMIN_BUTTONS if is_admin else REP_BUTTONS):
        kb.button(text=text, callback_data=cb)
    kb.adjust(1)
    return kb.as_markup()
