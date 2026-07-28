"""
Brand Bridge — Auth Pydantic Schemas
Request and Response models for all authentication endpoints.
Matches the documentation API spec exactly.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ═══════════════════════════════════════════════════════════════
# REQUEST SCHEMAS
# ═══════════════════════════════════════════════════════════════


class RegisterRequest(BaseModel):
    """POST /api/auth/register"""
    name: str = Field(..., min_length=2, max_length=255, examples=["Musa Ahmed"])
    email: EmailStr = Field(..., examples=["musa@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["SecurePass123"])
    password_confirmation: str = Field(..., examples=["SecurePass123"])
    role: str = Field(..., pattern="^(client|creator)$", examples=["creator"])

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, v, info):
        """Ensure password and password_confirmation match."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("পাসওয়ার্ড মিলছে না (passwords do not match)")
        return v


class LoginRequest(BaseModel):
    """POST /api/auth/login"""
    email: EmailStr = Field(..., examples=["musa@example.com"])
    password: str = Field(..., examples=["SecurePass123"])
    device_id: Optional[str] = Field(None, max_length=255, examples=["iPhone15-XYZ123"])


class VerifyEmailRequest(BaseModel):
    """POST /api/auth/verify-email"""
    email: EmailStr = Field(..., examples=["musa@example.com"])
    otp: str = Field(..., min_length=4, max_length=10, examples=["482917"])


class ResendOTPRequest(BaseModel):
    """POST /api/auth/resend-otp"""
    email: EmailStr = Field(..., examples=["musa@example.com"])


class ForgotPasswordRequest(BaseModel):
    """POST /api/auth/forgot-password"""
    email: EmailStr = Field(..., examples=["musa@example.com"])


class VerifyPasswordResetOTPRequest(BaseModel):
    """POST /api/auth/verify-password-reset-otp"""
    email: EmailStr = Field(..., examples=["musa@example.com"])
    otp: str = Field(..., min_length=4, max_length=10, examples=["482917"])


class ResetPasswordRequest(BaseModel):
    """POST /api/auth/reset-password"""
    email: EmailStr = Field(..., examples=["musa@example.com"])
    otp: str = Field(..., min_length=4, max_length=10, examples=["482917"])
    password: str = Field(..., min_length=6, max_length=128, examples=["NewSecurePass456"])
    password_confirmation: str = Field(..., examples=["NewSecurePass456"])

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("পাসওয়ার্ড মিলছে না (passwords do not match)")
        return v


# ═══════════════════════════════════════════════════════════════
# RESPONSE SCHEMAS
# ═══════════════════════════════════════════════════════════════


class UserResponse(BaseModel):
    """Serialized user data returned in API responses."""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    avatar: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    is_kyc_verified: bool
    is_two_step_enabled: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response for register and login — includes user + token."""
    user: UserResponse
    token: str
    message: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class OTPVerifyResponse(BaseModel):
    """Response for OTP verification endpoints."""
    message: str
    verified: bool = False


class PasswordResetOTPResponse(BaseModel):
    """Response for password reset OTP verification."""
    message: str
    token: Optional[str] = None
