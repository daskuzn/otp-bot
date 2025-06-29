from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import TimestampMixin, Base

class Partner(Base, TimestampMixin):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    shop_code = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    contact_name = Column(String(120), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    # relationships
    tasks = relationship("Task", back_populates="partner", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="partner", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Partner id={self.id} name={self.name}>"