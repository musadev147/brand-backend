"""
Brand Bridge — Profile & KYC SQLAlchemy Models
"""

import enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enums ─────────────────────────────────────────────────────
class PlatformType(str, enum.Enum):
    YOUTUBE = "YouTube"
    INSTAGRAM = "Instagram"
    TIKTOK = "TikTok"
    FACEBOOK = "Facebook"


class ContentType(str, enum.Enum):
    VIDEO = "video"
    IMAGE = "image"
    LINK = "link"


class KYCDocumentType(str, enum.Enum):
    NID = "nid"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    TRADE_LICENSE = "trade_license"


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ── Table 2: client_profiles ──────────────────────────────────
class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    business_type = Column(String(255), nullable=True)
    designation = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    budget_range = Column(Numeric(12, 2), default=0.00, nullable=False)
    business_number = Column(String(100), nullable=True)
    din_number = Column(String(100), nullable=True)
    tin_number = Column(String(100), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="client_profile")


# ── Table 3: creator_profiles ─────────────────────────────────
class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    followers_count = Column(Integer, default=0, nullable=False)
    avg_views = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    fake_followers_pct = Column(Integer, default=0, nullable=False)
    audience_quality_score = Column(Numeric(5, 2), default=0.00, nullable=False)
    audience_age_genders = Column(String(500), nullable=True)  # JSON-like string

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="creator_profile")
    categories = relationship("CreatorCategory", back_populates="creator_profile", cascade="all, delete-orphan")
    platform_links = relationship("CreatorPlatformLink", back_populates="creator_profile", cascade="all, delete-orphan")
    portfolio = relationship("CreatorPortfolio", back_populates="creator_profile", cascade="all, delete-orphan")
    reviews = relationship("CreatorReview", back_populates="creator_profile", cascade="all, delete-orphan")


# ── Table 4: creator_categories ───────────────────────────────
class CreatorCategory(Base):
    __tablename__ = "creator_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_profile_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    sub_category = Column(String(100), nullable=True)

    creator_profile = relationship("CreatorProfile", back_populates="categories")


# ── Table 5: creator_platform_links ───────────────────────────
class CreatorPlatformLink(Base):
    __tablename__ = "creator_platform_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_profile_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum(PlatformType, name="platformtype"), nullable=False)
    link = Column(String(500), nullable=False)
    followers = Column(Integer, default=0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    creator_profile = relationship("CreatorProfile", back_populates="platform_links")


# ── Table 6: creator_portfolio ────────────────────────────────
class CreatorPortfolio(Base):
    __tablename__ = "creator_portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_profile_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    url = Column(String(500), nullable=False)
    type = Column(Enum(ContentType, name="contenttype"), default=ContentType.LINK, nullable=False)

    creator_profile = relationship("CreatorProfile", back_populates="portfolio")


# ── Table 7: creator_reviews ──────────────────────────────────
class CreatorReview(Base):
    __tablename__ = "creator_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_profile_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    reviewer_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_id = Column(Integer, nullable=True)  # Can link to order later
    rating = Column(Numeric(3, 2), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    creator_profile = relationship("CreatorProfile", back_populates="reviews")
    reviewer = relationship("User")


# ── Table 8: kyc_documents ────────────────────────────────────
class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(Enum(KYCDocumentType, name="kycdocumenttype"), nullable=False)
    document_number = Column(String(100), nullable=False)
    front_image = Column(String(500), nullable=False)
    back_image = Column(String(500), nullable=True)
    selfie_image = Column(String(500), nullable=True)
    status = Column(Enum(KYCStatus, name="kycstatus"), default=KYCStatus.PENDING, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="kyc_documents")
