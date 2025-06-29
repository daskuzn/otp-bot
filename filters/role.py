# """Role‑based filters that берут данные напрямую из БД.

# Требования:
# • В `data` уже лежит `session` (AsyncSession) thanks to DBSessionMiddleware.
# • Фильтр сам читает роль из таблицы users (по telegram_id).
# • Положит найденного пользователя в `data["current_user"]`, чтобы хэндлеры могли
#   использовать его повторно без ещё одного запроса.
# """
# from typing import Any, Dict, Optional

# from aiogram.filters import BaseFilter
# from aiogram.types import TelegramObject
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from models.user import User, UserRole


# async def _get_user(session: AsyncSession, tg_id: int) -> Optional[User]:
#     """Fetch user by Telegram‑ID (cached per update if CurrentUserMiddleware not used)."""
#     stmt = select(User).where(User.telegram_id == tg_id)
#     return await session.scalar(stmt)


# class RoleFilter(BaseFilter):
#     """Generic filter: passes if user.role ∈ allowed_roles."""

#     def __init__(self, *allowed: UserRole):
#         self.allowed = set(allowed)

#     async def __call__(
#         self,
#         event: TelegramObject,
#         data: Dict[str, Any] | None = None,
#     ) -> bool:
#         if data is None:
#             return False  # no session, no user –> deny

#         session: AsyncSession | None = data.get("session")
#         if session is None:
#             return False

#         # Try to reuse current_user injected by other middleware
#         user: User | None = data.get("current_user")
#         if user is None and getattr(event, "from_user", None):
#             user = await _get_user(session, event.from_user.id)
#             # cache for later handlers in this update
#             if user is not None:
#                 data["current_user"] = user

#         return bool(user and user.role in self.allowed)


# class AdminFilter(RoleFilter):
#     """Разрешает только ADMIN‑пользователей."""

#     def __init__(self) -> None:  # noqa: D401
#         super().__init__(UserRole.ADMIN)


# class RepFilter(RoleFilter):
#     """Разрешает только REP‑пользователей."""

#     def __init__(self) -> None:  # noqa: D401
#         super().__init__(UserRole.REP)

# from __future__ import annotations

# from typing import Set

# from aiogram.filters import BaseFilter
# from aiogram.types import TelegramObject
# from sqlalchemy import select

# from database import async_session_factory  # глобальная фабрика сессий
# from models.user import User, UserRole


# class RoleFilter(BaseFilter):
#     """Generic role filter (без доступа к data)."""

#     allowed: Set[UserRole]

#     def __init__(self, *allowed: UserRole):
#         self.allowed = set(allowed)

#     async def __call__(self, event: TelegramObject, *_, **__) -> bool:  # noqa: D401
#         # event может быть Message или CallbackQuery
#         from_user = getattr(event, "from_user", None)
#         if not from_user:
#             return False

#         async with async_session_factory() as session:
#             user: User | None = await session.scalar(
#                 select(User).where(User.telegram_id == from_user.id)
#             )

#         return bool(user and user.role in self.allowed)


# class AdminFilter(RoleFilter):
#     """Пропускает только ADMIN‑пользователей."""

#     def __init__(self) -> None:  # noqa: D401
#         super().__init__(UserRole.ADMIN)


# class RepFilter(RoleFilter):
#     """Пропускает только REP‑пользователей."""

#     def __init__(self) -> None:  # noqa: D401
#         super().__init__(UserRole.REP)

# """Role‑based filters that берут данные напрямую из БД.

# Требования:
# • В `data` уже лежит `session` (AsyncSession) thanks to DBSessionMiddleware.
# • Фильтр сам читает роль из таблицы users (по telegram_id).
# • Положит найденного пользователя в `data["current_user"]`, чтобы хэндлеры могли
#   использовать его повторно без ещё одного запроса.
# """
# from typing import Any, Dict, Optional

# from aiogram.filters import BaseFilter
# from aiogram.types import TelegramObject
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from models.user import User, UserRole


# async def _get_user(session: AsyncSession, tg_id: int) -> Optional[User]:
#     """Fetch user by Telegram‑ID (cached per update if CurrentUserMiddleware not used)."""
#     stmt = select(User).where(User.telegram_id == tg_id)
#     return await session.scalar(stmt)


# class RoleFilter(BaseFilter):
#     """Generic filter: passes if user.role ∈ allowed_roles."""

#     def __init__(self, *allowed: UserRole):
#         self.allowed = set(allowed)

#     async def __call__(
#         self,
#         event: TelegramObject,
#         data: Dict[str, Any] | None = None,
#     ) -> bool:
#         if data is None:
#             return False  # no session, no user –> deny

#         session: AsyncSession | None = data.get("session")
#         if session is None:
#             return False

#         # Try to reuse current_user injected by other middleware
#         user: User | None = data.get("current_user")
#         if user is None and getattr(event, "from_user", None):
#             user = await _get_user(session, event.from_user.id)
#             # cache for later handlers in this update
#             if user is not None:
#                 data["current_user"] = user

#         return bool(user and user.role in self.allowed)


# class AdminFilter(RoleFilter):
#     """Разрешает только ADMIN‑пользователей."""

#     def __init__(self) -> None:  # noqa: D401
#         super().__init__(UserRole.ADMIN)


# class RepFilter(RoleFilter):
#     """Разрешает только REP‑пользователей."""

#     def __init__(self) -> None:  # noqa: D401
#         super().__init__(UserRole.REP)

# """Role‑based filters for aiogram 3 (single, correct definition)."""
# from typing import Any, Dict

# from aiogram.filters import BaseFilter
# from aiogram.types import TelegramObject

# from models.user import UserRole

# class AdminFilter(BaseFilter):
#     """Passes only if current_user.role == ADMIN."""

#     async def __call__(self, event: TelegramObject, data: Dict[str, Any]) -> bool:  # noqa: ANN401
#         user = data.get("current_user")  # injected by CurrentUserMiddleware
#         return bool(user and user.role == UserRole.ADMIN)

# class RepFilter(BaseFilter):
#     """Passes only if current_user.role == REP."""

#     async def __call__(self, event: TelegramObject, data: Dict[str, Any]) -> bool:  # noqa: ANN401
#         user = data.get("current_user")
#         return bool(user and user.role == UserRole.REP)

# """Role‑based filters compatible with aiogram 3 signature."""
# from typing import Any, Dict

# from aiogram.filters import BaseFilter
# from aiogram.types import TelegramObject

# from models.user import UserRole

# class AdminFilter(BaseFilter):
#     async def __call__(self, event: TelegramObject, data: Dict[str, Any]) -> bool:  # noqa: ANN401
#         user = data.get("current_user")
#         return bool(user and user.role == UserRole.ADMIN)

# class RepFilter(BaseFilter):
#     async def __call__(self, event: TelegramObject, data: Dict[str, Any]) -> bool:  # noqa: ANN401
#         user = data.get("current_user")
#         return bool(user and user.role == UserRole.REP)

# """Role‑based filters for handlers."""
# from aiogram.filters import BaseFilter
# from aiogram.types import Message

# from models.user import UserRole

# class AdminFilter(BaseFilter):
#     async def __call__(self, message: Message, current_user):  # injected by middleware
#         return current_user and current_user.role == UserRole.ADMIN

# class RepFilter(BaseFilter):
#     async def __call__(self, message: Message, current_user):
#         return current_user and current_user.role == UserRole.REP
# from __future__ import annotations
# from aiogram.filters import BaseFilter
# from aiogram.types import TelegramObject
# from sqlalchemy import select
# from database.db import async_session_factory
# from models.user import User, UserRole

# class RoleFilter(BaseFilter):
#     def __init__(self, *allowed: UserRole) -> None:
#         self.allowed = set(allowed)

#     async def __call__(self, event: TelegramObject, *_, **__) -> bool:
#         from_user = getattr(event, "from_user", None)
#         if not from_user:
#             return False

#         async with async_session_factory() as session:
#             user: User | None = await session.scalar(
#                 select(User).where(User.telegram_id == from_user.id)
#             )

#         return bool(user and user.role in self.allowed)

# AdminFilter = lambda: RoleFilter(UserRole.ADMIN)
# RepFilter   = lambda: RoleFilter(UserRole.REP)
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
