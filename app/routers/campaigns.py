from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.campaign import CampaignStatus
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.services import campaign_service

router = APIRouter(prefix="/campaigns", tags=["🎯 Campaign Management"])

@router.post(
    "/create",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="নতুন Campaign তৈরি",
    description="নতুন campaign তৈরি করে। (শুধুমাত্র Client রোলের জন্য প্রযোজ্য)",
)
def create_campaign(
    request: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্লায়েন্টদের জন্য অনুমোদিত (Allowed for clients only)",
        )
    return campaign_service.create_campaign(db, current_user.id, request)

@router.get(
    "",
    response_model=List[CampaignResponse],
    summary="সব Campaign List",
    description="ক্যাম্পেইনের লিস্ট রিটার্ন করে। ফিল্টার এবং পেজিনেশন সাপোর্ট করে।",
)
def get_campaigns(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return campaign_service.get_campaigns(db, status, page, limit)

@router.get(
    "/{id}",
    response_model=CampaignResponse,
    summary="Single Campaign Details",
    description="নির্দিষ্ট ক্যাম্পেইনের বিস্তারিত তথ্য রিটার্ন করে।",
)
def get_campaign(
    id: int,
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign_by_id(db, id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ক্যাম্পেইন পাওয়া যায়নি (Campaign not found)",
        )
    return campaign

@router.put(
    "/{id}/update",
    response_model=CampaignResponse,
    summary="Campaign Edit",
    description="ক্যাম্পেইন তথ্য আপডেট করে। (শুধুমাত্র ক্যাম্পেইনের মালিক/ক্লায়েন্ট করতে পারবে)",
)
def update_campaign(
    id: int,
    request: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign_by_id(db, id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ক্যাম্পেইন পাওয়া যায়নি (Campaign not found)",
        )
    if campaign.client_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই ক্যাম্পেইনের মালিক নন (You do not own this campaign)",
        )
    return campaign_service.update_campaign(db, campaign, request)

@router.delete(
    "/{id}/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Campaign Delete",
    description="ক্যাম্পেইন ডিলেট করে।",
)
def delete_campaign(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign_by_id(db, id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ক্যাম্পেইন পাওয়া যায়নি (Campaign not found)",
        )
    if campaign.client_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই ক্যাম্পেইনের মালিক নন (You do not own this campaign)",
        )
    campaign_service.delete_campaign(db, campaign)
    return None

@router.put(
    "/{id}/status",
    response_model=CampaignResponse,
    summary="Status Change",
    description="ক্যাম্পেইনের স্ট্যাটাস পরিবর্তন করে।",
)
def change_campaign_status(
    id: int,
    status_param: CampaignStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign_by_id(db, id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ক্যাম্পেইন পাওয়া যায়নি (Campaign not found)",
        )
    if campaign.client_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই ক্যাম্পেইনের মালিক নন (You do not own this campaign)",
        )
    
    update_schema = CampaignUpdate(status=status_param)
    return campaign_service.update_campaign(db, campaign, update_schema)
