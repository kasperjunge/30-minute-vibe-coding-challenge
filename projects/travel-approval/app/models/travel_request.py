"""TravelRequest model - core entity representing a travel approval request."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class TravelRequest(Base):
    """Travel Request model for pre-trip approval workflow."""

    __tablename__ = "travel_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    request_type = Column(String, nullable=False)  # operations, project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Travel details
    destination = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    purpose = Column(Text, nullable=False)
    estimated_cost = Column(Numeric(10, 2), nullable=False)

    # Budget tracking
    taccount_id = Column(Integer, ForeignKey("t_accounts.id"), nullable=False, index=True)

    # Approval workflow
    status = Column(String, default="pending", nullable=False, index=True)  # pending, approved, rejected
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approval_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    requester = relationship("User", back_populates="travel_requests", foreign_keys=[requester_id])
    approver = relationship("User", back_populates="approval_requests", foreign_keys=[approver_id])
    project = relationship("Project", back_populates="travel_requests")
    taccount = relationship("TAccount", back_populates="travel_requests")
    notifications = relationship("Notification", back_populates="travel_request")

    def __repr__(self):
        return f"<TravelRequest #{self.id} - {self.destination} ({self.status})>"
