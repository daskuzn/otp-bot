from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .base import TimestampMixin, Base

class CompetitorOffer(Base, TimestampMixin):
    __tablename__ = "competitor_offers"

    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False)
    competitor_name = Column(String(120), nullable=False)
    product_details = Column(Text, nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)

    visit = relationship("Visit", back_populates="competitor_offers")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CompetitorOffer id={self.id} visit={self.visit_id}>"