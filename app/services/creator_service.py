from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User, UserRole
from app.models.profile import CreatorProfile, CreatorCategory, CreatorPlatformLink

def search_creators(
    db: Session,
    query_str: Optional[str] = None,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    platform: Optional[str] = None,
    location: Optional[str] = None,
    min_followers: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
) -> List[User]:
    # Start query from User model filtering for role='creator'
    query = db.query(User).filter(User.role == UserRole.CREATOR, User.deleted_at.is_(None))
    
    # Join CreatorProfile since most filters belong to it
    query = query.join(User.creator_profile)
    
    if query_str:
        # Search in User name or CreatorProfile bio
        query = query.filter(
            or_(
                User.name.ilike(f"%{query_str}%"),
                CreatorProfile.bio.ilike(f"%{query_str}%")
            )
        )
        
    if category:
        # Filter by Category
        query = query.filter(
            CreatorProfile.categories.any(CreatorCategory.category.ilike(category))
        )

    if sub_category:
        # Filter by Sub-Category
        query = query.filter(
            CreatorProfile.categories.any(CreatorCategory.sub_category.ilike(sub_category))
        )
        
    if platform:
        # Filter by Platform Link presence
        query = query.filter(
            CreatorProfile.platform_links.any(CreatorPlatformLink.platform == platform)
        )
        
    if location:
        # Filter by location in profile
        query = query.filter(CreatorProfile.location.ilike(f"%{location}%"))
        
    if min_followers is not None:
        query = query.filter(CreatorProfile.followers_count >= min_followers)
        
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

def get_creator_public_profile(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(
        User.id == user_id, 
        User.role == UserRole.CREATOR,
        User.deleted_at.is_(None)
    ).first()
