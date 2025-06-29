# from aiogram.utils.keyboard import InlineKeyboardBuilder

# REP_MENU_BUTTONS = [
#     ("📅 Мои визиты на сегодня", "visits_today"),
#     ("🛍️ Запланировать визит", "plan_visit"),
#     ("📍 Отправить отчёт о визите", "start_report"),
#     ("📊 Моя статистика", "stats"),
#     ("❓ Помощь", "help"),
# ]

# ADMIN_MENU_BUTTONS = [
#     ("👤 Представители", "admin_reps"),
#     ("🧾 Отчёты", "admin_reports"),
#     ("⚠️ Нестандартные визиты", "admin_alerts"),
#     ("📊 Аналитика", "admin_analytics"),
#     ("📤 Экспорт", "admin_export"),
# ]

# def main_menu(is_admin: bool = False):
#     kb = InlineKeyboardBuilder()
#     for text, cb in ADMIN_MENU_BUTTONS if is_admin else REP_MENU_BUTTONS:
#         kb.button(text=text, callback_data=cb)
#     kb.adjust(1)
#     return kb.as_markup()

from aiogram.utils.keyboard import InlineKeyboardBuilder

REP_BUTTONS = [
    ("📅 Мои визиты на сегодня",   "visits_today"),
    ("🛍️ Запланировать визит",     "plan_visit"),
    ("📍 Отправить отчёт о визите", "start_report"),
    ("📊 Моя статистика",          "stats"),
    ("❓ Помощь",                  "help"),
]

ADMIN_BUTTONS = [
    ("👤 Представители",           "admin_reps"),
    ("🧾 Отчёты",                  "admin_reports"),
    ("⚠️ Нестандартные визиты",    "admin_alerts"),
    ("📊 Аналитика",               "admin_analytics"),
    ("📤 Экспорт",                 "admin_export"),
]

def main_menu(is_admin: bool):
    kb = InlineKeyboardBuilder()
    for text, cb in (ADMIN_BUTTONS if is_admin else REP_BUTTONS):
        kb.button(text=text, callback_data=cb)
    kb.adjust(1)
    return kb.as_markup()
