import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

class ContractStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PAID = "paid"
    RELEASED = "released"

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_key = Column(String(100), unique=True, nullable=False)
    client_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    gig_id = Column(Integer, ForeignKey("gigs.id", ondelete="SET NULL"), nullable=True)
    
    is_starred_by_client = Column(Boolean, default=False, nullable=False)
    is_starred_by_creator = Column(Boolean, default=False, nullable=False)
    
    last_message_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    client = relationship("User", foreign_keys=[client_user_id])
    creator = relationship("User", foreign_keys=[creator_user_id])
    campaign = relationship("Campaign")
    gig = relationship("Gig")
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatThread(id={self.id}, chat_key='{self.chat_key}')>"

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_thread_id = Column(Integer, ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_role = Column(String(20), nullable=False)  # 'client' or 'creator'
    text = Column(Text, nullable=False)
    
    # Contract details
    is_contract = Column(Boolean, default=False, nullable=False)
    contract_title = Column(String(255), nullable=True)
    contract_budget = Column(Numeric(12, 2), nullable=True)
    contract_deadline = Column(String(100), nullable=True)
    contract_status = Column(Enum(ContractStatus, name="contractstatus"), nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    thread = relationship("ChatThread", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_user_id])

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, thread_id={self.chat_thread_id}, sender={self.sender_user_id})>"
