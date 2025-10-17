from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    app_name: str = "FastAPI Template"
    debug: bool = True
    database_url: str = "sqlite:///./data/app.db"
    host: str = "0.0.0.0"
    port: int = 8000
    session_secret_key: str = "change-this-in-production-to-a-random-secret-key"
    session_max_age: int = 30 * 24 * 60 * 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()

