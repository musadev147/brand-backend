"""
Brand Bridge — KYC Router
Endpoints for submitting KYC verification documents and checking verification status.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import KYCDocumentResponse, KYCSubmitRequest
from app.services import kyc_service

router = APIRouter(prefix="/kyc", tags=["🪪 KYC Verification"])


# ── 1. Submit KYC ─────────────────────────────────────────────
@router.post(
    "/submit",
    response_model=KYCDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit KYC Verification",
    description="KYC ভেরিফিকেশনের জন্য ডকুমেন্ট (NID/Passport/Driving License/Trade License) এবং ইমেজ সাবমিট করে।",
)
def submit_kyc(
    request: KYCSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kyc_doc = kyc_service.submit_kyc_document(db, current_user, request)
    return KYCDocumentResponse.model_validate(kyc_doc)


# ── 2. Get KYC Status ─────────────────────────────────────────
@router.get(
    "/status",
    response_model=KYCDocumentResponse,
    summary="Get KYC Verification Status",
    description="ইউজারের সাবমিট করা সর্বশেষ KYC ডকুমেন্টের বর্তমান ভেরিফিকেশন স্ট্যাটাস (pending/approved/rejected) রিটার্ন করে।",
)
def get_kyc_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kyc_doc = kyc_service.get_latest_kyc_document(db, current_user)
    if not kyc_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="কোনো KYC ডকুমেন্ট সাবমিট করা হয়নি (No KYC document submitted yet)",
        )
    return KYCDocumentResponse.model_validate(kyc_doc)
