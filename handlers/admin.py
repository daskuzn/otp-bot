# from aiogram import Router, F
# from aiogram.types import CallbackQuery
# from filters.role import AdminFilter
# from keyboards.main_menu import main_menu

# router = Router()

# @router.callback_query(AdminFilter(), F.data == "admin_reps")
# async def show_reps(call: CallbackQuery):
#     await call.message.answer("Список представителей (в разработке)")
from aiogram import Router, F
from aiogram.types import CallbackQuery
from filters.role import AdminFilter

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_reps")
async def show_reps(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Список представителей (в разработке)")