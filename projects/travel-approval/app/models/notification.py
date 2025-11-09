"""Notification model - in-app notifications for workflow events."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Notification(Base):
    """Notification model for in-app notifications."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    travel_request_id = Column(Integer, ForeignKey("travel_requests.id"), nullable=False)
    notification_type = Column(String, nullable=False)  # request_submitted, request_approved, request_rejected
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
    travel_request = relationship("TravelRequest", back_populates="notifications")

    def __repr__(self):
        return f"<Notification #{self.id} - {self.notification_type} for User {self.user_id}>"
