from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.models.chat import ContractStatus
from app.schemas.auth import UserResponse

class ChatThreadCreate(BaseModel):
    creator_user_id: int
    campaign_id: Optional[int] = None
    gig_id: Optional[int] = None

class ChatThreadResponse(BaseModel):
    id: int
    chat_key: str
    client_user_id: int
    creator_user_id: int
    campaign_id: Optional[int] = None
    gig_id: Optional[int] = None
    is_starred_by_client: bool
    is_starred_by_creator: bool
    last_message_at: Optional[datetime] = None
    created_at: datetime
    client: Optional[UserResponse] = None
    creator: Optional[UserResponse] = None

    model_config = {"from_attributes": True}

class ChatMessageSend(BaseModel):
    thread_id: int
    text: str

class ContractSend(BaseModel):
    thread_id: int
    contract_title: str = Field(..., max_length=255)
    contract_budget: Decimal = Field(..., ge=0)
    contract_deadline: str = Field(..., max_length=100)

class ContractRespond(BaseModel):
    status: ContractStatus = Field(..., description="accepted, rejected, paid, or released")

class ChatMessageResponse(BaseModel):
    id: int
    chat_thread_id: int
    sender_user_id: int
    sender_role: str
    text: str
    is_contract: bool
    contract_title: Optional[str] = None
    contract_budget: Optional[Decimal] = None
    contract_deadline: Optional[str] = None
    contract_status: Optional[ContractStatus] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
