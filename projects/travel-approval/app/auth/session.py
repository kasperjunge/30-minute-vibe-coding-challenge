"""Session management using signed cookies."""

from datetime import datetime, timedelta
from typing import Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import settings


class SessionManager:
    """Manage user sessions with signed cookies."""

    def __init__(self):
        self.serializer = URLSafeTimedSerializer(settings.secret_key)
        self.max_age = settings.session_max_age

    def create_session(self, user_id: int) -> str:
        """
        Create a signed session token for a user.

        Args:
            user_id: User ID to encode in session

        Returns:
            Signed session token
        """
        return self.serializer.dumps({"user_id": user_id})

    def verify_session(self, session_token: str) -> Optional[int]:
        """
        Verify a session token and extract user ID.

        Args:
            session_token: Signed session token

        Returns:
            User ID if valid, None if invalid or expired
        """
        try:
            data = self.serializer.loads(session_token, max_age=self.max_age)
            return data.get("user_id")
        except (BadSignature, SignatureExpired):
            return None


# Global session manager instance
session_manager = SessionManager()
