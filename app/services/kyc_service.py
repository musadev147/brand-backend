"""
Brand Bridge — KYC Service
Business logic for KYC (Know Your Customer) document submissions.
"""

from typing import Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.profile import KYCDocument, KYCStatus
from app.schemas.profile import KYCSubmitRequest


def submit_kyc_document(db: Session, user: User, data: KYCSubmitRequest) -> KYCDocument:
    """Submit a new KYC verification request."""
    # Create new KYC document record
    kyc_doc = KYCDocument(
        user_id=user.id,
        document_type=data.document_type,
        document_number=data.document_number,
        front_image=data.front_image,
        back_image=data.back_image,
        selfie_image=data.selfie_image,
        status=KYCStatus.PENDING,
    )
    db.add(kyc_doc)
    db.commit()
    db.refresh(kyc_doc)
    return kyc_doc


def get_latest_kyc_document(db: Session, user: User) -> Optional[KYCDocument]:
    """Retrieve the latest KYC document submitted by the user."""
    return db.query(KYCDocument)\
             .filter(KYCDocument.user_id == user.id)\
             .order_by(desc(KYCDocument.created_at))\
             .first()
