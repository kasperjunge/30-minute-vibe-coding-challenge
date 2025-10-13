"""
Session model for tracking breathing practice sessions
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Session(Base):
    """
    Session model for recording individual breathing practice sessions.
    """

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pattern_id = Column(Integer, ForeignKey("breathing_patterns.id"), nullable=False)

    # Duration tracking (in seconds)
    target_duration = Column(Integer, nullable=False)  # 120, 300, or 600
    actual_duration = Column(Integer, nullable=False, default=0)

    # Completion tracking
    completed_at = Column(DateTime, nullable=False, index=True)
    is_completed = Column(Boolean, default=False, nullable=False)

    # Timezone information
    timezone = Column(String, nullable=False, default="UTC")

    # Relationships
    user = relationship("User", back_populates="sessions")
    pattern = relationship("BreathingPattern", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, pattern_id={self.pattern_id}, completed={self.is_completed})>"
