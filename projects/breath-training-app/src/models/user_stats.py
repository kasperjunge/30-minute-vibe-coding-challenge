"""
User Statistics model for tracking practice progress
"""

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database import Base


class UserStats(Base):
    """
    User statistics model for aggregated practice data.
    """

    __tablename__ = "user_stats"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)

    # Practice statistics
    total_sessions = Column(Integer, default=0, nullable=False)
    total_minutes = Column(Integer, default=0, nullable=False)

    # Streak tracking
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_practice_date = Column(Date, nullable=True)

    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="stats")

    def __repr__(self):
        return f"<UserStats(user_id={self.user_id}, sessions={self.total_sessions}, streak={self.current_streak})>"
