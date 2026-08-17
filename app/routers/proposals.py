from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.campaign import ProposalStatus
from app.schemas.campaign import ProposalCreate, ProposalResponse, ProposalUpdateStatus
from app.services import campaign_service

router = APIRouter(prefix="/proposals", tags=["📨 Proposal Management"])

@router.post(
    "/submit",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Proposal Submit করো",
    description="ক্যাম্পেইনে প্রপোজাল সাবমিট করে। (শুধুমাত্র Creator রোলের জন্য প্রযোজ্য)",
)
def submit_proposal(
    request: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CREATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্রিয়েটরদের জন্য অনুমোদিত (Allowed for creators only)",
        )
    return campaign_service.submit_proposal(db, current_user.id, request)

@router.get(
    "/campaign/{campaign_id}",
    response_model=List[ProposalResponse],
    summary="Campaign এর সব Proposals",
    description="নির্দিষ্ট ক্যাম্পেইনে জমা হওয়া সব প্রপোজাল লিস্ট রিটার্ন করে। (ক্যাম্পেইনের মালিক/ক্লায়েন্টের জন্য প্রযোজ্য)",
)
def get_campaign_proposals(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign_by_id(db, campaign_id)
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
    
    return campaign_service.get_proposals_for_campaign(db, campaign_id)

@router.put(
    "/{id}/status",
    response_model=ProposalResponse,
    summary="Accept/Reject Proposal",
    description="প্রপোজাল স্ট্যাটাস পরিবর্তন করে (accepted/rejected)।",
)
def respond_to_proposal(
    id: int,
    request: ProposalUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find proposal and verify that current user is the client who owns the campaign
    proposal = db.query(campaign_service.Proposal).filter(campaign_service.Proposal.id == id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="প্রপোজাল পাওয়া যায়নি (Proposal not found)",
        )
    
    campaign = campaign_service.get_campaign_by_id(db, proposal.campaign_id)
    if campaign.client_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই ক্যাম্পেইনের মালিক নন (You do not own this campaign)",
        )
    
    return campaign_service.respond_to_proposal(db, id, request.status)

@router.get(
    "/my",
    response_model=List[ProposalResponse],
    summary="আমার Submit করা Proposals",
    description="লগইন করা ক্রিয়েটরের সাবমিট করা সব প্রপোজাল লিস্ট রিটার্ন করে।",
)
def get_my_proposals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CREATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্রিয়েটরদের জন্য অনুমোদিত (Allowed for creators only)",
        )
    return campaign_service.get_creator_proposals(db, current_user.id)
