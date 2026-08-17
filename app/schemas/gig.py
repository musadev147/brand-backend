from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class GigBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str
    price: Decimal = Field(..., ge=0)
    delivery_time: str = Field(..., max_length=100)
    platform: str = Field(..., max_length=100)
    social_link: Optional[str] = Field(None, max_length=500)
    banner_image: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., max_length=100)
    region: Optional[str] = Field(None, max_length=255)
    deliverables: Optional[str] = None
    revisions: str = Field("2 Revisions", max_length=50)

    # Social stats
    youtube_link: Optional[str] = Field(None, max_length=500)
    tiktok_link: Optional[str] = Field(None, max_length=500)
    facebook_link: Optional[str] = Field(None, max_length=500)
    instagram_link: Optional[str] = Field(None, max_length=500)

    youtube_followers: int = Field(0, ge=0)
    tiktok_followers: int = Field(0, ge=0)
    facebook_followers: int = Field(0, ge=0)
    instagram_followers: int = Field(0, ge=0)

    video_url: Optional[str] = Field(None, max_length=500)
    views_count: int = Field(0, ge=0)

class GigCreate(GigBase):
    pass

class GigUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    delivery_time: Optional[str] = Field(None, max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    social_link: Optional[str] = Field(None, max_length=500)
    banner_image: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=255)
    deliverables: Optional[str] = None
    revisions: Optional[str] = Field(None, max_length=50)
    
    youtube_link: Optional[str] = Field(None, max_length=500)
    tiktok_link: Optional[str] = Field(None, max_length=500)
    facebook_link: Optional[str] = Field(None, max_length=500)
    instagram_link: Optional[str] = Field(None, max_length=500)
    
    youtube_followers: Optional[int] = Field(None, ge=0)
    tiktok_followers: Optional[int] = Field(None, ge=0)
    facebook_followers: Optional[int] = Field(None, ge=0)
    instagram_followers: Optional[int] = Field(None, ge=0)
    
    video_url: Optional[str] = Field(None, max_length=500)
    views_count: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class GigResponse(GigBase):
    id: int
    creator_user_id: int
    verified_followers: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SocialVerifyRequest(BaseModel):
    platform: str = Field(..., description="YouTube, Instagram, TikTok, Facebook")
    url: str = Field(..., description="Profile/Channel Link")

class SocialVerifyResponse(BaseModel):
    channel_name: str
    followers: int
    is_verified: bool
