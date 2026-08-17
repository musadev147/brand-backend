from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.gig import (
    GigCreate,
    GigUpdate,
    GigResponse,
    SocialVerifyRequest,
    SocialVerifyResponse,
)
from app.services import gig_service

router = APIRouter(prefix="/gigs", tags=["🎨 Gig Marketplace"])

@router.post(
    "/create",
    response_model=GigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="নতুন Gig তৈরি",
    description="নতুন গিগ সার্ভিস তৈরি করে। (শুধুমাত্র Creator রোলের জন্য প্রযোজ্য)",
)
def create_gig(
    request: GigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CREATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্রিয়েটরদের জন্য অনুমোদিত (Allowed for creators only)",
        )
    return gig_service.create_gig(db, current_user.id, request)

@router.get(
    "",
    response_model=List[GigResponse],
    summary="সব Gig List",
    description="মার্কেটপ্লেসে থাকা সকল সক্রিয় গিগের তালিকা রিটার্ন করে। ফিল্টার ও পেজিনেশন সাপোর্ট করে।",
)
def get_gigs(
    category: Optional[str] = None,
    platform: Optional[str] = None,
    region: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return gig_service.get_gigs(db, category, platform, region, page, limit)

@router.get(
    "/{id}",
    response_model=GigResponse,
    summary="Single Gig Details",
    description="নির্দিষ্ট গিগের বিস্তারিত তথ্য এবং সোশ্যাল মিডিয়া স্ট্যাটাস রিটার্ন করে।",
)
def get_gig(
    id: int,
    db: Session = Depends(get_db),
):
    gig = gig_service.get_gig_by_id(db, id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="গিগ পাওয়া যায়নি (Gig not found)",
        )
    return gig

@router.put(
    "/{id}/update",
    response_model=GigResponse,
    summary="Gig Edit",
    description="গিগের প্রাইজ, বর্ণনা বা অন্যান্য তথ্য আপডেট করে। (শুধুমাত্র গিগের মালিক করতে পারবে)",
)
def update_gig(
    id: int,
    request: GigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    gig = gig_service.get_gig_by_id(db, id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="গিগ পাওয়া যায়নি (Gig not found)",
        )
    if gig.creator_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই গিগের মালিক নন (You do not own this gig)",
        )
    return gig_service.update_gig(db, gig, request)

@router.delete(
    "/{id}/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Gig Delete",
    description="গিগ ডিলেট করে।",
)
def delete_gig(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    gig = gig_service.get_gig_by_id(db, id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="গিগ পাওয়া যায়নি (Gig not found)",
        )
    if gig.creator_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই গিগের মালিক নন (You do not own this gig)",
        )
    gig_service.delete_gig(db, gig)
    return None

@router.post(
    "/verify-social",
    response_model=SocialVerifyResponse,
    summary="Social Link Verify (Scraper)",
    description="ক্রিয়েটরের সোশ্যাল মিডিয়া লিংক ভেরিফাই করে ফলোয়ার কাউন্ট ও ইউজার নেম রিটার্ন করে।",
)
def verify_social(
    request: SocialVerifyRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.CREATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্রিয়েটরদের জন্য অনুমোদিত (Allowed for creators only)",
        )
    result = gig_service.verify_social_link(request.platform, request.url)
    return SocialVerifyResponse(**result)
