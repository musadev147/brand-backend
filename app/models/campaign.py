import enum
from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

class CampaignStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Numeric(12, 2), nullable=False)
    deadline = Column(Date, nullable=False)
    platform = Column(String(100), nullable=False)
    content_type = Column(String(100), nullable=False)
    requirements = Column(Text, nullable=True)
    status = Column(Enum(CampaignStatus, name="campaignstatus"), default=CampaignStatus.OPEN, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    client = relationship("User", foreign_keys=[client_user_id])
    proposals = relationship("Proposal", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, title='{self.title}', status='{self.status}')>"

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    delivery_time = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(ProposalStatus, name="proposalstatus"), default=ProposalStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="proposals")
    creator = relationship("User", foreign_keys=[creator_user_id])

    def __repr__(self) -> str:
        return f"<Proposal(id={self.id}, campaign_id={self.campaign_id}, status='{self.status}')>"
