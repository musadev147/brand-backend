from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileResponse, CreatorProfileResponse
from app.schemas.auth import UserResponse
from app.services import creator_service

router = APIRouter(prefix="/creators", tags=["🔍 Creator Search & Discovery"])

@router.get(
    "/search",
    response_model=List[ProfileResponse],
    summary="Creator Search / Discover",
    description="মার্কেটপ্লেসের বিভিন্ন ক্রিয়েটরদের সার্চ ও ফিল্টার করে তালিকা রিটার্ন করে।",
)
def search_creators(
    q: Optional[str] = None,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    platform: Optional[str] = None,
    location: Optional[str] = None,
    min_followers: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    creators = creator_service.search_creators(
        db=db,
        query_str=q,
        category=category,
        sub_category=sub_category,
        platform=platform,
        location=location,
        min_followers=min_followers,
        page=page,
        limit=limit,
    )
    
    results = []
    for creator in creators:
        user_data = UserResponse.model_validate(creator)
        profile_data = None
        if creator.creator_profile:
            profile_data = CreatorProfileResponse.model_validate(creator.creator_profile)
        results.append(ProfileResponse(user=user_data, profile=profile_data))
        
    return results

@router.get(
    "/{id}/profile",
    response_model=ProfileResponse,
    summary="Creator Public Profile",
    description="নির্দিষ্ট ক্রিয়েটরের পাবলিক প্রোফাইল বিবরণ রিটার্ন করে।",
)
def get_creator_profile(
    id: int,
    db: Session = Depends(get_db),
):
    creator = creator_service.get_creator_public_profile(db, id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ক্রিয়েটর পাওয়া যায়নি (Creator not found)",
        )
    
    user_data = UserResponse.model_validate(creator)
    profile_data = None
    if creator.creator_profile:
        profile_data = CreatorProfileResponse.model_validate(creator.creator_profile)
        
    return ProfileResponse(user=user_data, profile=profile_data)
