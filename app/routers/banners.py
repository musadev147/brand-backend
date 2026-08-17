from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.banner import PromoBanner
from app.schemas.banner import PromoBannerResponse

router = APIRouter(prefix="/banners", tags=["🏠 Home Promo Banners"])

@router.get(
    "",
    response_model=List[PromoBannerResponse],
    summary="স্লাইডার ব্যানার লিস্ট",
    description="হোম পেজের স্লাইডার কারোসেলের জন্য সকল একটিভ প্রোমো ব্যানারগুলোর তালিকা রিটার্ন করে।",
)
def get_promo_banners(db: Session = Depends(get_db)):
    return db.query(PromoBanner).filter(PromoBanner.is_active == True).order_by(PromoBanner.sort_order.asc()).all()
