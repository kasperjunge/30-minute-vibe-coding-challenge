import pytest
from sqlalchemy.orm import Session


def test_database_session(test_db):
    """Test that database session is created"""
    assert test_db is not None
    assert isinstance(test_db, Session)
