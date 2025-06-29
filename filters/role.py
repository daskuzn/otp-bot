from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from sqlalchemy import select
from common.ctx import current_session
from models.user import User, UserRole



class RoleFilter(BaseFilter):
    def __init__(self, allowed: UserRole):
        self.allowed = allowed

    async def __call__(self, event: TelegramObject) -> bool:
        user_id = getattr(event.from_user, "id", None)
        if not user_id:
            return False

        session = current_session.get()
        if session is None:
            return False

        user: User | None = await session.scalar(
            select(User).where(User.telegram_id == user_id)
        )
        return bool(user and user.role == self.allowed)

AdminFilter = lambda: RoleFilter(UserRole.ADMIN)   # noqa: E731
RepFilter   = lambda: RoleFilter(UserRole.REP)     # noqa: E731
