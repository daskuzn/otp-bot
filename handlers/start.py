""" /start – регистрация пользователя + меню. """
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole
from keyboards.main_menu import main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    temp_msg = await message.answer("Проверка пользователя...")
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    user = await session.scalar(stmt)

    if not user:
        # новый пользователь → создаём репрезентативную запись
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            role=UserRole.REP,          # по умолчанию – представитель
        )
        session.add(user)
        await session.flush()

    msg = await temp_msg.edit_text(
        "Добро пожаловать! Главное меню ниже:",
        reply_markup=main_menu(is_admin=user.role == UserRole.ADMIN),
    )
