"""
Tests for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


def test_app_starts(client):
    """
    Test that the application starts correctly.
    """
    assert app.title == "Breath Training App"


def test_health_check(client):
    """
    Test the health check endpoint returns 200 and correct response.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
