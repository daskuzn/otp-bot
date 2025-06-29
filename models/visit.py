from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    rep_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)
    visited_at = Column(DateTime(timezone=True), nullable=False)
    marketing_checked = Column(Boolean, default=False, nullable=True)
    satisfaction_done = Column(Boolean, default=False, nullable=True)
    competitor_logged = Column(Boolean, default=False, nullable=True)
    notes = Column(Text, nullable=True)
    report_id = Column(Integer, ForeignKey("report.id", ondelete="CASCADE"), nullable=False)

    # relationships
    rep = relationship("User", back_populates="visits")
    partner = relationship("Partner", back_populates="visits")
    
    report = relationship(
        "Report", back_populates="visit"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Visit id={self.id} rep={self.rep_id} partner={self.partner_id}>"
