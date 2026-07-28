"""
Brand Bridge — Auth Service
All business logic for authentication flows:
  register, login, verify email, forgot/reset password, logout.
"""

from typing import Optional, Tuple

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.user import PasswordReset, User, UserRole
from app.utils.otp import generate_otp, get_otp_expiry, is_otp_expired
from app.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


# ═══════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════

def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str,
) -> tuple[User, str, str]:
    """
    Register a new user.

    Returns:
        Tuple of (user, access_token, otp_code).
        OTP is returned for dev console logging (in production, send via email).
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="এই ইমেইল দিয়ে আগেই অ্যাকাউন্ট আছে (Email already registered)",
        )

    # Create user
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        is_email_verified=False,
    )
    db.add(user)
    db.flush()  # Get the user ID before commit

    # Generate email verification OTP
    otp_code = generate_otp()
    otp_record = PasswordReset(
        email=email,
        otp=otp_code,
        expires_at=get_otp_expiry(),
    )
    db.add(otp_record)
    db.commit()
    db.refresh(user)

    # Create JWT token
    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return user, token, otp_code


# ═══════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════

def login_user(
    db: Session,
    email: str,
    password: str,
    device_id: Optional[str] = None,
) -> tuple[User, str]:
    """
    Authenticate a user with email and password.

    Returns:
        Tuple of (user, access_token).

    Raises:
        HTTPException 401 if credentials are wrong.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ভুল ইমেইল বা পাসওয়ার্ড (Invalid email or password)",
        )

    # Check soft delete
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকাউন্টটি মুছে ফেলা হয়েছে (Account has been deleted)",
        )

    # Update device_id if provided
    if device_id:
        user.device_id = device_id
        db.commit()

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return user, token


# ═══════════════════════════════════════════════════════════════
# EMAIL VERIFICATION
# ═══════════════════════════════════════════════════════════════

def verify_email_otp(db: Session, email: str, otp: str) -> User:
    """
    Verify user's email with OTP code.

    Returns:
        The verified User object.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ইউজার পাওয়া যায়নি (User not found)",
        )

    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ইমেইল আগেই ভেরিফাই করা হয়েছে (Email already verified)",
        )

    # Find latest OTP for this email
    otp_record = (
        db.query(PasswordReset)
        .filter(PasswordReset.email == email, PasswordReset.is_verified == False)
        .order_by(desc(PasswordReset.created_at))
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="কোনো OTP পাওয়া যায়নি (No OTP found, request a new one)",
        )

    if is_otp_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP মেয়াদ শেষ হয়ে গেছে (OTP expired, request a new one)",
        )

    if otp_record.otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ভুল OTP কোড (Invalid OTP code)",
        )

    # Mark OTP as verified
    otp_record.is_verified = True

    # Mark user email as verified
    user.is_email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return user


def resend_email_otp(db: Session, email: str) -> str:
    """
    Generate and store a new OTP for email verification.

    Returns:
        The new OTP code (for dev logging).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ইউজার পাওয়া যায়নি (User not found)",
        )

    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ইমেইল আগেই ভেরিফাই করা হয়েছে (Email already verified)",
        )

    otp_code = generate_otp()
    otp_record = PasswordReset(
        email=email,
        otp=otp_code,
        expires_at=get_otp_expiry(),
    )
    db.add(otp_record)
    db.commit()

    return otp_code


# ═══════════════════════════════════════════════════════════════
# FORGOT / RESET PASSWORD
# ═══════════════════════════════════════════════════════════════

def forgot_password(db: Session, email: str) -> str:
    """
    Initiate password reset by generating an OTP.

    Returns:
        The OTP code (for dev logging).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="এই ইমেইলে কোনো অ্যাকাউন্ট নেই (No account found with this email)",
        )

    otp_code = generate_otp()
    otp_record = PasswordReset(
        email=email,
        otp=otp_code,
        expires_at=get_otp_expiry(),
    )
    db.add(otp_record)
    db.commit()

    return otp_code


def verify_password_reset_otp(db: Session, email: str, otp: str) -> str:
    """
    Verify the OTP for password reset.

    Returns:
        A temporary reset token (JWT with short expiry).
    """
    otp_record = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.email == email,
            PasswordReset.is_verified == False,
        )
        .order_by(desc(PasswordReset.created_at))
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="কোনো OTP পাওয়া যায়নি (No OTP found)",
        )

    if is_otp_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP মেয়াদ শেষ (OTP expired)",
        )

    if otp_record.otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ভুল OTP কোড (Invalid OTP code)",
        )

    # Mark as verified
    otp_record.is_verified = True
    db.commit()

    # Generate short-lived reset token (15 minutes)
    from datetime import timedelta
    reset_token = create_access_token(
        data={"sub": email, "type": "password_reset"},
        expires_delta=timedelta(minutes=15),
    )

    return reset_token


def reset_password(db: Session, email: str, otp: str, new_password: str) -> None:
    """
    Reset user's password after OTP verification.

    Validates that the OTP was previously verified.
    """
    # Check for verified OTP
    otp_record = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.email == email,
            PasswordReset.otp == otp,
            PasswordReset.is_verified == True,
        )
        .order_by(desc(PasswordReset.created_at))
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP ভেরিফাই করা হয়নি বা ভুল (OTP not verified or invalid)",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ইউজার পাওয়া যায়নি (User not found)",
        )

    # Update password
    user.password = hash_password(new_password)
    db.commit()


# ═══════════════════════════════════════════════════════════════
# GET USER BY ID
# ═══════════════════════════════════════════════════════════════

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a user by their primary key."""
    return db.query(User).filter(User.id == user_id).first()
