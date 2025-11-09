"""TAccount model - represents budget accounts for tracking travel expenses."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class TAccount(Base):
    """T-Account model for budget allocation and tracking."""

    __tablename__ = "t_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String, unique=True, nullable=False)  # e.g., "T-1234"
    account_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    travel_requests = relationship("TravelRequest", back_populates="taccount")

    def __repr__(self):
        return f"<TAccount {self.account_code} - {self.account_name}>"
