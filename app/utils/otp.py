"""
Brand Bridge — OTP Utilities
Generates and validates One-Time Passwords for email verification
and password reset flows.
"""

import random
import string
from datetime import datetime, timedelta, timezone

from app.config import get_settings

settings = get_settings()


def generate_otp(length: int = 6) -> str:
    """
    Generate a random numeric OTP code.

    Args:
        length: Number of digits (default 6).

    Returns:
        A string of random digits, e.g. '482917'.
    """
    return "".join(random.choices(string.digits, k=length))


def get_otp_expiry() -> datetime:
    """
    Get the expiry datetime for a new OTP.

    Returns:
        UTC datetime = now + OTP_EXPIRE_MINUTES from settings.
    """
    return datetime.now(timezone.utc) + timedelta(
        minutes=settings.OTP_EXPIRE_MINUTES
    )


def is_otp_expired(expires_at: datetime) -> bool:
    """
    Check if an OTP has expired.

    Args:
        expires_at: The stored expiry datetime.

    Returns:
        True if expired, False if still valid.
    """
    now = datetime.now(timezone.utc)
    # Handle naive datetimes (from SQLite)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return now > expires_at
