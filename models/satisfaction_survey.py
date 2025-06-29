from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import TimestampMixin, Base

class SatisfactionSurvey(Base, TimestampMixin):
    __tablename__ = "satisfaction_surveys"

    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)

    visit = relationship("Visit", back_populates="satisfaction_surveys")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SatisfactionSurvey id={self.id} visit={self.visit_id}>"