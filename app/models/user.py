"""
Brand Bridge — User & PasswordReset SQLAlchemy Models

Matches the documentation schema exactly:
- Table 1: users (18 columns)
- Table 18: password_resets
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    func,
)

from app.database import Base


# ── Enums ─────────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    """User roles in the system."""
    CLIENT = "client"
    CREATOR = "creator"


# ── Table 1: users ───────────────────────────────────────────
class User(Base):
    """
    User model — the core identity table.
    Both Clients and Creators share this table with role differentiation.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum("client", "creator", name="userrole"), nullable=False)
    avatar = Column(String(500), nullable=True)

    # Verification flags
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    is_kyc_verified = Column(Boolean, default=False, nullable=False)

    # Security settings
    is_two_step_enabled = Column(Boolean, default=False, nullable=False)
    is_fingerprint_enabled = Column(Boolean, default=False, nullable=False)
    is_face_verification_enabled = Column(Boolean, default=False, nullable=False)
    is_phone_otp_enabled = Column(Boolean, default=False, nullable=False)

    email_verified_at = Column(DateTime, nullable=True)
    remember_token = Column(String(100), nullable=True)
    device_id = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    @property
    def is_active(self) -> bool:
        """User is active if not soft-deleted."""
        return self.deleted_at is None


# ── Table 18: password_resets ────────────────────────────────
class PasswordReset(Base):
    """
    Stores OTP codes for both email verification and password reset.
    OTPs expire after OTP_EXPIRE_MINUTES.
    """
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True)
    otp = Column(String(10), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PasswordReset(email='{self.email}', otp='{self.otp}')>"

    @property
    def is_expired(self) -> bool:
        """Check if the OTP has expired."""
        return datetime.utcnow() > self.expires_at
