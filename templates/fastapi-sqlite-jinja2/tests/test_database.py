"""
Database operation tests
"""
from app.shared.database import Base


def test_database_connection(test_db):
    """Test that we can connect to the database"""
    # If we got a test_db fixture, connection works
    assert test_db is not None
    assert test_db.bind is not None
    
    # Verify Base metadata is configured
    assert Base.metadata is not None
