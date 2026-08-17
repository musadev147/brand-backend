from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.campaign import CampaignStatus, ProposalStatus
from app.schemas.auth import UserResponse

class CampaignBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    product_name: str = Field(..., min_length=2, max_length=255)
    description: str
    budget: Decimal = Field(..., ge=0)
    deadline: date
    platform: str = Field(..., max_length=100)
    content_type: str = Field(..., max_length=100)
    requirements: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    product_name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    deadline: Optional[date] = None
    platform: Optional[str] = Field(None, max_length=100)
    content_type: Optional[str] = Field(None, max_length=100)
    requirements: Optional[str] = None
    status: Optional[CampaignStatus] = None

class CampaignResponse(CampaignBase):
    id: int
    client_user_id: int
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ProposalBase(BaseModel):
    price: Decimal = Field(..., ge=0)
    delivery_time: str = Field(..., max_length=100)
    message: str

class ProposalCreate(ProposalBase):
    campaign_id: int

class ProposalUpdateStatus(BaseModel):
    status: ProposalStatus

class ProposalResponse(ProposalBase):
    id: int
    campaign_id: int
    creator_user_id: int
    status: ProposalStatus
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserResponse] = None

    model_config = {"from_attributes": True}
