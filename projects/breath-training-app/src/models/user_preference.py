"""
User Preferences model for storing user settings
"""

from datetime import datetime, time

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from src.database import Base


class UserPreference(Base):
    """
    User preferences model for storing user-specific settings.
    """

    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)

    # Pattern preferences
    default_pattern_id = Column(Integer, ForeignKey("breathing_patterns.id"), nullable=True)

    # Audio preferences
    audio_enabled = Column(Boolean, default=True, nullable=False)

    # Reminder preferences
    reminder_enabled = Column(Boolean, default=False, nullable=False)
    reminder_time = Column(Time, nullable=True)

    # Onboarding status
    has_completed_onboarding = Column(Boolean, default=False, nullable=False)

    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="preferences")
    default_pattern = relationship("BreathingPattern", foreign_keys=[default_pattern_id])

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, audio_enabled={self.audio_enabled})>"
