from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

class Gig(Base):
    __tablename__ = "gigs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    delivery_time = Column(String(100), nullable=False)
    platform = Column(String(100), nullable=False)
    social_link = Column(String(500), nullable=True)
    verified_followers = Column(Integer, default=0, nullable=False)
    banner_image = Column(String(500), nullable=True)
    category = Column(String(100), nullable=False)
    region = Column(String(255), nullable=True)
    deliverables = Column(Text, nullable=True)
    revisions = Column(String(50), default="2 Revisions", nullable=False)
    
    # Social stats
    youtube_link = Column(String(500), nullable=True)
    tiktok_link = Column(String(500), nullable=True)
    facebook_link = Column(String(500), nullable=True)
    instagram_link = Column(String(500), nullable=True)
    
    youtube_followers = Column(Integer, default=0, nullable=False)
    tiktok_followers = Column(Integer, default=0, nullable=False)
    facebook_followers = Column(Integer, default=0, nullable=False)
    instagram_followers = Column(Integer, default=0, nullable=False)
    
    video_url = Column(String(500), nullable=True)
    views_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_user_id])

    def __repr__(self) -> str:
        return f"<Gig(id={self.id}, title='{self.title}', price={self.price})>"
