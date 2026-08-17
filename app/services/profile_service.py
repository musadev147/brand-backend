"""
Brand Bridge — Profile Service
Business logic for managing Client & Creator profiles and security settings.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.profile import (
    ClientProfile,
    CreatorProfile,
    CreatorCategory,
    CreatorPlatformLink,
    CreatorPortfolio,
)
from app.schemas.profile import ClientProfileUpdate, CreatorProfileUpdate, SecuritySettingsUpdate


def get_or_create_client_profile(db: Session, user_id: int) -> ClientProfile:
    """Retrieve client profile or create one if it doesn't exist."""
    profile = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
    if not profile:
        profile = ClientProfile(
            user_id=user_id,
            company_name="My Company",  # Default placeholder matching model non-null requirement
            business_type="Agency",
            budget_range=0.00,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_or_create_creator_profile(db: Session, user_id: int) -> CreatorProfile:
    """Retrieve creator profile or create one if it doesn't exist."""
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()
    if not profile:
        profile = CreatorProfile(
            user_id=user_id,
            bio="",
            location="",
            followers_count=0,
            avg_views=0,
            engagement_rate=0.00,
            fake_followers_pct=0,
            audience_quality_score=0.00,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_user_profile(db: Session, user: User):
    """Get the full user profile including client or creator details."""
    if user.role == "client":
        profile = get_or_create_client_profile(db, user.id)
    else:
        profile = get_or_create_creator_profile(db, user.id)
    return profile


def update_client_profile(db: Session, user: User, data: ClientProfileUpdate) -> ClientProfile:
    """Update client profile fields."""
    profile = get_or_create_client_profile(db, user.id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile


def update_creator_profile(db: Session, user: User, data: CreatorProfileUpdate) -> CreatorProfile:
    """Update creator profile fields, categories, links, and portfolio."""
    profile = get_or_create_creator_profile(db, user.id)
    
    # 1. Update basic fields
    update_data = data.model_dump(exclude_unset=True)
    basic_fields = [
        "bio", "location", "followers_count", "avg_views", 
        "engagement_rate", "fake_followers_pct", "audience_quality_score", 
        "audience_age_genders"
    ]
    for field in basic_fields:
        if field in update_data and update_data[field] is not None:
            setattr(profile, field, update_data[field])

    # 2. Update Categories
    if data.categories is not None:
        # Clear existing
        db.query(CreatorCategory).filter(CreatorCategory.creator_profile_id == profile.id).delete()
        # Add new
        for cat_name in data.categories:
            db.add(CreatorCategory(creator_profile_id=profile.id, category=cat_name))

    # 3. Update Platform Links
    if data.platform_links is not None:
        # Clear existing
        db.query(CreatorPlatformLink).filter(CreatorPlatformLink.creator_profile_id == profile.id).delete()
        # Add new
        for link in data.platform_links:
            db.add(CreatorPlatformLink(
                creator_profile_id=profile.id,
                platform=link.platform,
                link=link.link,
                followers=link.followers,
                is_verified=link.is_verified,
            ))

    # 4. Update Portfolio Items
    if data.portfolio is not None:
        # Clear existing
        db.query(CreatorPortfolio).filter(CreatorPortfolio.creator_profile_id == profile.id).delete()
        # Add new
        for port in data.portfolio:
            db.add(CreatorPortfolio(
                creator_profile_id=profile.id,
                title=port.title,
                url=port.url,
                type=port.type,
            ))

    db.commit()
    db.refresh(profile)
    return profile


def update_security_settings(db: Session, user: User, data: SecuritySettingsUpdate) -> User:
    """Update security/settings flags for a user."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    return user


def update_avatar(db: Session, user: User, avatar_url: str) -> User:
    """Update the user's profile picture URL."""
    user.avatar = avatar_url
    db.commit()
    db.refresh(user)
    return user
