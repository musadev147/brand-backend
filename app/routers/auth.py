"""
Brand Bridge — Auth Router
All 8 authentication endpoints as defined in the documentation.

Endpoints:
  POST /api/auth/register
  POST /api/auth/login
  POST /api/auth/verify-email
  POST /api/auth/resend-otp
  POST /api/auth/forgot-password
  POST /api/auth/verify-password-reset-otp
  POST /api/auth/reset-password
  POST /api/auth/logout
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    OTPVerifyResponse,
    PasswordResetOTPResponse,
    RegisterRequest,
    ResendOTPRequest,
    ResetPasswordRequest,
    UserResponse,
    VerifyEmailRequest,
    VerifyPasswordResetOTPRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])


# ── 1. Register ───────────────────────────────────────────────
@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="নতুন User Registration",
    description="নতুন user তৈরি করে, JWT token এবং email verification OTP দেয়।",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user, token, otp_code = auth_service.register_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role,
    )

    # 📧 Send OTP via Resend
    from app.utils.email import send_otp_email
    send_otp_email(
        to_email=request.email, 
        otp_code=otp_code, 
        subject="Brand Bridge - Email Verification OTP"
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
        message=f"রেজিস্ট্রেশন সফল! ইমেইলে OTP পাঠানো হয়েছে। (Registration successful! OTP: {otp_code})",
    )


# ── 2. Login ──────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User Login",
    description="ইমেইল ও পাসওয়ার্ড দিয়ে login করে JWT token পায়।",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user, token = auth_service.login_user(
        db=db,
        email=request.email,
        password=request.password,
        device_id=request.device_id,
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
        message="লগইন সফল! (Login successful!)",
    )


# ── 3. Verify Email ──────────────────────────────────────────
@router.post(
    "/verify-email",
    response_model=OTPVerifyResponse,
    summary="Email OTP Verify",
    description="রেজিস্ট্রেশনের পর ইমেইলে পাঠানো OTP দিয়ে verify করে।",
)
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    auth_service.verify_email_otp(
        db=db,
        email=request.email,
        otp=request.otp,
    )

    return OTPVerifyResponse(
        message="ইমেইল ভেরিফিকেশন সফল! (Email verified successfully!)",
        verified=True,
    )


# ── 4. Resend OTP ────────────────────────────────────────────
@router.post(
    "/resend-otp",
    response_model=MessageResponse,
    summary="OTP আবার পাঠান",
    description="নতুন OTP জেনারেট করে ইমেইলে পাঠায়।",
)
def resend_otp(request: ResendOTPRequest, db: Session = Depends(get_db)):
    otp_code = auth_service.resend_email_otp(db=db, email=request.email)

    # 📧 Send via Resend
    from app.utils.email import send_otp_email
    send_otp_email(
        to_email=request.email, 
        otp_code=otp_code, 
        subject="Brand Bridge - New Email Verification OTP"
    )

    return MessageResponse(
        message=f"নতুন OTP পাঠানো হয়েছে! (New OTP sent! OTP: {otp_code})",
    )


# ── 5. Forgot Password ───────────────────────────────────────
@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Password Reset Request",
    description="পাসওয়ার্ড রিসেটের জন্য OTP পাঠায়।",
)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    otp_code = auth_service.forgot_password(db=db, email=request.email)

    # 📧 Send via Resend
    from app.utils.email import send_otp_email
    send_otp_email(
        to_email=request.email, 
        otp_code=otp_code, 
        subject="Brand Bridge - Password Reset OTP"
    )

    return MessageResponse(
        message=f"পাসওয়ার্ড রিসেট OTP পাঠানো হয়েছে! (Password reset OTP sent! OTP: {otp_code})",
    )


# ── 6. Verify Password Reset OTP ─────────────────────────────
@router.post(
    "/verify-password-reset-otp",
    response_model=PasswordResetOTPResponse,
    summary="Reset OTP Verify",
    description="পাসওয়ার্ড রিসেটের OTP verify করে এবং reset token দেয়।",
)
def verify_password_reset_otp(
    request: VerifyPasswordResetOTPRequest,
    db: Session = Depends(get_db),
):
    reset_token = auth_service.verify_password_reset_otp(
        db=db,
        email=request.email,
        otp=request.otp,
    )

    return PasswordResetOTPResponse(
        message="OTP ভেরিফাই সফল! এখন নতুন পাসওয়ার্ড সেট করুন। (OTP verified! Set new password now.)",
        token=reset_token,
    )


# ── 7. Reset Password ────────────────────────────────────────
@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="নতুন Password সেট",
    description="OTP verify করার পর নতুন পাসওয়ার্ড সেট করে।",
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service.reset_password(
        db=db,
        email=request.email,
        otp=request.otp,
        new_password=request.password,
    )

    return MessageResponse(
        message="পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে! (Password reset successful!)",
    )


# ── 8. Logout ─────────────────────────────────────────────────
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="বর্তমান session থেকে logout করে। (Client-side token discard)",
)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint.

    Note: With stateless JWT, the actual invalidation happens client-side
    by discarding the token. For production, implement a token blacklist
    using Redis.
    """
    return MessageResponse(
        message=f"লগআউট সফল! ({current_user.name}, you have been logged out)",
    )
