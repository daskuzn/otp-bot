from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

# The import "from aiogram_calendar import SimpleCalendar, simple_cal_callback" is incorrect if the package is not installed.
# Make sure you have installed the "aiogram-calendar" package:
# pip install aiogram-calendar

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

choose_date_kb = SimpleCalendar().start_calendar()

# after date choose we will offer partners list dynamically in router