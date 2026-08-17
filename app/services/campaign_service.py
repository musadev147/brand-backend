from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.campaign import Campaign, Proposal, CampaignStatus, ProposalStatus
from app.schemas.campaign import CampaignCreate, CampaignUpdate, ProposalCreate
from app.models.user import User

def create_campaign(db: Session, client_id: int, schema: CampaignCreate) -> Campaign:
    campaign = Campaign(
        client_user_id=client_id,
        title=schema.title,
        product_name=schema.product_name,
        description=schema.description,
        budget=schema.budget,
        deadline=schema.deadline,
        platform=schema.platform,
        content_type=schema.content_type,
        requirements=schema.requirements,
        status=CampaignStatus.OPEN,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

def get_campaigns(
    db: Session, 
    status_filter: Optional[str] = None, 
    page: int = 1, 
    limit: int = 20
) -> List[Campaign]:
    query = db.query(Campaign)
    if status_filter:
        query = query.filter(Campaign.status == status_filter)
    
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

def get_campaign_by_id(db: Session, campaign_id: int) -> Optional[Campaign]:
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()

def update_campaign(db: Session, campaign: Campaign, schema: CampaignUpdate) -> Campaign:
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)
    db.commit()
    db.refresh(campaign)
    return campaign

def delete_campaign(db: Session, campaign: Campaign) -> None:
    db.delete(campaign)
    db.commit()

def submit_proposal(db: Session, creator_id: int, schema: ProposalCreate) -> Proposal:
    # Check if campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == schema.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ক্যাম্পেইন পাওয়া যায়নি (Campaign not found)"
        )
    
    # Check if proposal already submitted
    existing = db.query(Proposal).filter(
        Proposal.campaign_id == schema.campaign_id,
        Proposal.creator_user_id == creator_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="আপনি ইতিমধ্যে এই ক্যাম্পেইনে প্রপোজাল পাঠিয়েছেন (Already submitted a proposal)"
        )
    
    proposal = Proposal(
        campaign_id=schema.campaign_id,
        creator_user_id=creator_id,
        price=schema.price,
        delivery_time=schema.delivery_time,
        message=schema.message,
        status=ProposalStatus.PENDING,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal

def get_proposals_for_campaign(db: Session, campaign_id: int) -> List[Proposal]:
    return db.query(Proposal).filter(Proposal.campaign_id == campaign_id).all()

def respond_to_proposal(db: Session, proposal_id: int, new_status: ProposalStatus) -> Proposal:
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="প্রপোজাল পাওয়া যায়নি (Proposal not found)"
        )
    proposal.status = new_status
    db.commit()
    db.refresh(proposal)
    return proposal

def get_creator_proposals(db: Session, creator_id: int) -> List[Proposal]:
    return db.query(Proposal).filter(Proposal.creator_user_id == creator_id).all()
