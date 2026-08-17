from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class PromoBanner(Base):
    __tablename__ = "promo_banners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=False)
    button_text = Column(String(100), default="Learn More", nullable=False)
    redirect_to = Column(String(255), default="/", nullable=False)
    icon_name = Column(String(100), nullable=True)  # e.g., 'store', 'star', 'campaign'
    background_gradient = Column(String(255), nullable=True)  # e.g., 'linear-gradient(135deg, #6366f1, #a855f7)'
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<PromoBanner(id={self.id}, title='{self.title}')>"
