"""
Breathing Pattern model for defining breathing exercise patterns
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class BreathingPattern(Base):
    """
    Breathing pattern model storing timing and metadata for breathing exercises.
    """

    __tablename__ = "breathing_patterns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)

    # Timing parameters (in seconds)
    inhale_duration = Column(Integer, nullable=False)
    inhale_hold_duration = Column(Integer, nullable=False, default=0)
    exhale_duration = Column(Integer, nullable=False)
    exhale_hold_duration = Column(Integer, nullable=False, default=0)

    # Pattern type
    is_preset = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="custom_patterns")
    sessions = relationship("Session", back_populates="pattern")

    def __repr__(self):
        return f"<BreathingPattern(id={self.id}, name={self.name}, timing={self.inhale_duration}-{self.inhale_hold_duration}-{self.exhale_duration}-{self.exhale_hold_duration})>"
