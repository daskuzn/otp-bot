# from aiogram import Router, F
# from aiogram.filters import Command
# from aiogram.types import CallbackQuery, Message

# from keyboards.main_menu import main_menu
# from filters.role import AdminFilter, RepFilter

# router = Router()

# @router.message(Command("menu"))
# async def show_menu(message: Message, current_user):
#     await message.answer(
#         "Главное меню:",
#         reply_markup=main_menu(is_admin=current_user.role == current_user.role.ADMIN),
#     )

# @router.callback_query(F.data == "help")
# async def help_cb(call: CallbackQuery):
#     await call.answer("Обратитесь в службу поддержки.")

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.main_menu import main_menu
from filters.role import AdminFilter, RepFilter

router = Router()

# /menu или любой текст → выводим меню
@router.message()
async def show_menu(msg: Message):
    # для примера показываем меню репа; если у вас есть фильтр роли, передайте флаг
    await msg.answer("Главное меню:", reply_markup=main_menu(is_admin=False))

# ---------- callback-хэндлеры представителя ----------
@router.callback_query(RepFilter(), F.data == "visits_today")
async def visits_today(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("📅 Визиты на сегодня: пока пусто")

@router.callback_query(RepFilter(), F.data == "plan_visit")
async def plan_visit(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("🛍️ Планирование визита (в разработке)")

@router.callback_query(RepFilter(), F.data == "start_report")
async def start_report(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("📍 Отчёт о визите (в разработке)")

@router.callback_query(RepFilter(), F.data == "stats")
async def stats(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("📊 Статистика (в разработке)")

@router.callback_query(RepFilter(), F.data == "help")
async def help_rep(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("❓ Помощь: напишите администратору.")

# ---------- callback-хэндлеры администратора ----------
@router.callback_query(AdminFilter(), F.data == "admin_reps")
async def admin_reps(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("👤 Список представителей (в разработке)")

@router.callback_query(AdminFilter(), F.data == "admin_reports")
async def admin_reports(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("🧾 Все отчёты (в разработке)")

@router.callback_query(AdminFilter(), F.data == "admin_alerts")
async def admin_alerts(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("⚠️ Нестандартные визиты (в разработке)")

@router.callback_query(AdminFilter(), F.data == "admin_analytics")
async def admin_analytics(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("📊 Аналитика (в разработке)")

@router.callback_query(AdminFilter(), F.data == "admin_export")
async def admin_export(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("📤 Экспорт отчётов (в разработке)")
