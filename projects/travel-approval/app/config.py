"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./travel_approval.db"

    # Security
    secret_key: str = "change-this-secret-key-in-production"
    session_cookie_name: str = "travel_approval_session"
    session_max_age: int = 86400  # 24 hours in seconds

    # Application
    app_name: str = "Travel Approval System"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
