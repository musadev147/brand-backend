"""
Brand Bridge — Profile & KYC Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl

from app.models.profile import PlatformType, ContentType, KYCDocumentType, KYCStatus
from app.schemas.auth import UserResponse


# ── Client Profile Schemas ────────────────────────────────────
class ClientProfileResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    business_type: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    budget_range: Decimal
    business_number: Optional[str] = None
    din_number: Optional[str] = None
    tin_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=255)
    business_type: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    budget_range: Optional[Decimal] = Field(None, ge=0)
    business_number: Optional[str] = Field(None, max_length=100)
    din_number: Optional[str] = Field(None, max_length=100)
    tin_number: Optional[str] = Field(None, max_length=100)


# ── Creator Profile Nested Schemas ────────────────────────────
class CreatorCategorySchema(BaseModel):
    id: Optional[int] = None
    category: str = Field(..., max_length=100)
    sub_category: Optional[str] = Field(None, max_length=100)

    model_config = {"from_attributes": True}


class CreatorPlatformLinkSchema(BaseModel):
    id: Optional[int] = None
    platform: PlatformType
    link: str = Field(..., max_length=500)
    followers: int = Field(0, ge=0)
    is_verified: bool = False

    model_config = {"from_attributes": True}


class CreatorPortfolioSchema(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=255)
    url: str = Field(..., max_length=500)
    type: ContentType = ContentType.LINK

    model_config = {"from_attributes": True}


class CreatorReviewSchema(BaseModel):
    id: int
    reviewer_user_id: Optional[int]
    reviewer_name: Optional[str] = None
    reviewer_avatar: Optional[str] = None
    rating: Decimal
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Creator Profile Schemas ───────────────────────────────────
class CreatorProfileResponse(BaseModel):
    id: int
    user_id: int
    bio: Optional[str] = None
    location: Optional[str] = None
    followers_count: int
    avg_views: int
    engagement_rate: Decimal
    fake_followers_pct: int
    audience_quality_score: Decimal
    audience_age_genders: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    categories: List[CreatorCategorySchema] = []
    platform_links: List[CreatorPlatformLinkSchema] = []
    portfolio: List[CreatorPortfolioSchema] = []
    reviews: List[CreatorReviewSchema] = []

    model_config = {"from_attributes": True}


class CreatorProfileUpdate(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    followers_count: Optional[int] = Field(None, ge=0)
    avg_views: Optional[int] = Field(None, ge=0)
    engagement_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    fake_followers_pct: Optional[int] = Field(None, ge=0, le=100)
    audience_quality_score: Optional[Decimal] = Field(None, ge=0, le=100)
    audience_age_genders: Optional[str] = Field(None, max_length=500)
    categories: Optional[List[str]] = None
    platform_links: Optional[List[CreatorPlatformLinkSchema]] = None
    portfolio: Optional[List[CreatorPortfolioSchema]] = None


# ── Combined Profile Response ─────────────────────────────────
class ProfileResponse(BaseModel):
    user: UserResponse
    profile: Optional[Union[ClientProfileResponse, CreatorProfileResponse]] = None


# ── KYC Schemas ───────────────────────────────────────────────
class KYCSubmitRequest(BaseModel):
    document_type: KYCDocumentType
    document_number: str = Field(..., min_length=5, max_length=100)
    front_image: str = Field(..., max_length=500)
    back_image: Optional[str] = Field(None, max_length=500)
    selfie_image: Optional[str] = Field(None, max_length=500)


class KYCDocumentResponse(BaseModel):
    id: int
    user_id: int
    document_type: KYCDocumentType
    document_number: str
    front_image: str
    back_image: Optional[str] = None
    selfie_image: Optional[str] = None
    status: KYCStatus
    rejection_reason: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Security Settings Schema ──────────────────────────────────
class SecuritySettingsUpdate(BaseModel):
    is_two_step_enabled: Optional[bool] = None
    is_fingerprint_enabled: Optional[bool] = None
    is_face_verification_enabled: Optional[bool] = None
    is_phone_otp_enabled: Optional[bool] = None
