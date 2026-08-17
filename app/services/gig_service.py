from typing import List, Optional
from sqlalchemy.orm import Session
import re

from app.models.gig import Gig
from app.schemas.gig import GigCreate, GigUpdate

def create_gig(db: Session, creator_id: int, schema: GigCreate) -> Gig:
    # Calculate verified followers from active social link count or platform followers
    followers = 0
    if schema.platform.lower() == "youtube":
        followers = schema.youtube_followers
    elif schema.platform.lower() == "instagram":
        followers = schema.instagram_followers
    elif schema.platform.lower() == "tiktok":
        followers = schema.tiktok_followers
    elif schema.platform.lower() == "facebook":
        followers = schema.facebook_followers
    else:
        followers = schema.youtube_followers + schema.instagram_followers + schema.tiktok_followers + schema.facebook_followers
        
    gig = Gig(
        creator_user_id=creator_id,
        title=schema.title,
        description=schema.description,
        price=schema.price,
        delivery_time=schema.delivery_time,
        platform=schema.platform,
        social_link=schema.social_link,
        verified_followers=followers,
        banner_image=schema.banner_image,
        category=schema.category,
        region=schema.region,
        deliverables=schema.deliverables,
        revisions=schema.revisions,
        
        youtube_link=schema.youtube_link,
        tiktok_link=schema.tiktok_link,
        facebook_link=schema.facebook_link,
        instagram_link=schema.instagram_link,
        
        youtube_followers=schema.youtube_followers,
        tiktok_followers=schema.tiktok_followers,
        facebook_followers=schema.facebook_followers,
        instagram_followers=schema.instagram_followers,
        
        video_url=schema.video_url,
        views_count=schema.views_count,
        is_active=True,
    )
    db.add(gig)
    db.commit()
    db.refresh(gig)
    return gig

def get_gigs(
    db: Session,
    category: Optional[str] = None,
    platform: Optional[str] = None,
    region: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> List[Gig]:
    query = db.query(Gig).filter(Gig.is_active == True)
    if category:
        query = query.filter(Gig.category == category)
    if platform:
        query = query.filter(Gig.platform == platform)
    if region:
        query = query.filter(Gig.region == region)
        
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

def get_gig_by_id(db: Session, gig_id: int) -> Optional[Gig]:
    return db.query(Gig).filter(Gig.id == gig_id).first()

def update_gig(db: Session, gig: Gig, schema: GigUpdate) -> Gig:
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(gig, key, value)
        
    # Re-calculate followers if followers fields are updated
    if any(k in update_data for k in ["youtube_followers", "instagram_followers", "tiktok_followers", "facebook_followers", "platform"]):
        followers = 0
        if gig.platform.lower() == "youtube":
            followers = gig.youtube_followers
        elif gig.platform.lower() == "instagram":
            followers = gig.instagram_followers
        elif gig.platform.lower() == "tiktok":
            followers = gig.tiktok_followers
        elif gig.platform.lower() == "facebook":
            followers = gig.facebook_followers
        else:
            followers = gig.youtube_followers + gig.instagram_followers + gig.tiktok_followers + gig.facebook_followers
        gig.verified_followers = followers
        
    db.commit()
    db.refresh(gig)
    return gig

def delete_gig(db: Session, gig: Gig) -> None:
    db.delete(gig)
    db.commit()

def verify_social_link(platform: str, url: str) -> dict:
    """
    Mock social verification parser.
    Extracts user/channel name from url and returns realistic statistics.
    """
    # Simple extraction
    match = re.search(r'(?:github|youtube|instagram|facebook|twitter|tiktok)\.com/([^/?#]+)', url, re.IGNORECASE)
    username = match.group(1) if match else "creator_channel"
    
    # Static realistic follower/subscriber outputs depending on username length
    mock_followers = (len(username) * 7412) + 25000
    
    return {
        "channel_name": username.replace("@", "").title(),
        "followers": mock_followers,
        "is_verified": True
    }
