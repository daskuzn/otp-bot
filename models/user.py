from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import TimestampMixin, Base
from ._types import pg_enum
from .enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(32), nullable=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    role = Column(pg_enum(UserRole, "userrole"), nullable=False, server_default=UserRole.REP.value)

    # relationships
    tasks = relationship("Task", back_populates="rep", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="rep", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} tg={self.telegram_id}>"