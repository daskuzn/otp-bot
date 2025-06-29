from sqlalchemy import ForeignKey, Integer, Text, Column, Identity, Enum
from sqlalchemy.orm import relationship

from models.enums import Marketing as marketing_enum
from models.base import Base

class Report(Base):

    __tablename__ = "report"

    id = Column(Integer, Identity(always=True), primary_key=True)
    photos_list = Column(Text, nullable=False)
    marketing = Column(
        Enum(
            marketing_enum,
            name="marketing",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    interview = Column(Text, nullable=False)
    share = Column(Integer, nullable=False)
    competitors = Column(Text, nullable=False)
    comment = Column(Text, nullable=True)
    task_id = Column(
        Integer, 
        ForeignKey("tasks.id", ondelete="CASCADE"), 
        nullable=False,
        unique=True,
    )

    visit = relationship(
        "Visit",
        back_populates="report",
        cascade="all, delete-orphan",
        uselist=False,
    )

    task = relationship(
        "Task",
        back_populates="report",
        uselist=False,
    )
