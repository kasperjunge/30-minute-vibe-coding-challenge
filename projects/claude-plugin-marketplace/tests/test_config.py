import os
import pytest
from app.shared.config import Settings


def test_settings_defaults():
    """Test that settings load with defaults"""
    settings = Settings()
    
    assert settings.app_name == "FastAPI Template"
    assert settings.debug is True
    assert settings.database_url == "sqlite:///./data/app.db"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_settings_override_with_env(monkeypatch):
    """Test that environment variables override defaults"""
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("PORT", "9000")
    
    settings = Settings()
    
    assert settings.app_name == "Test App"
    assert settings.debug is False
    assert settings.port == 9000


def test_settings_case_insensitive(monkeypatch):
    """Test that environment variables are case insensitive"""
    monkeypatch.setenv("app_name", "Lowercase Test")
    
    settings = Settings()
    
    assert settings.app_name == "Lowercase Test"

