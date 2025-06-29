import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import TimestampMixin, Base

class Visit(Base, TimestampMixin):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    rep_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)
    visited_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    marketing_checked = Column(Boolean, default=False, nullable=False)
    satisfaction_done = Column(Boolean, default=False, nullable=False)
    competitor_logged = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)

    # relationships
    rep = relationship("User", back_populates="visits")
    partner = relationship("Partner", back_populates="visits")
    competitor_offers = relationship(
        "CompetitorOffer", back_populates="visit", cascade="all, delete-orphan"
    )
    satisfaction_surveys = relationship(
        "SatisfactionSurvey", back_populates="visit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Visit id={self.id} rep={self.rep_id} partner={self.partner_id}>"