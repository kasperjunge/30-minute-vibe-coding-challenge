"""Plugin models for the marketplace."""
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from app.shared.database import Base


class Plugin(Base):
    """Plugin model representing a plugin in the marketplace."""
    
    __tablename__ = "plugins"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    author = relationship("User", backref="plugins")
    versions = relationship("PluginVersion", back_populates="plugin", cascade="all, delete-orphan")


class PluginVersion(Base):
    """Plugin version model representing a specific version of a plugin."""
    
    __tablename__ = "plugin_versions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("plugins.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    readme_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    plugin_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    plugin = relationship("Plugin", back_populates="versions")

