"""
Brand Bridge — Profile Router
Endpoints for viewing/updating user profiles and toggling security settings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse
from app.schemas.profile import (
    ClientProfileResponse,
    CreatorProfileResponse,
    ClientProfileUpdate,
    CreatorProfileUpdate,
    ProfileResponse,
    SecuritySettingsUpdate,
)
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["👤 Profile Management"])


class AvatarUpdateRequest(BaseModel):
    avatar_url: str = Field(..., description="URL of the uploaded avatar image")


# ── 1. Get Profile ────────────────────────────────────────────
@router.get(
    "",
    response_model=ProfileResponse,
    summary="Get Current User Profile",
    description="লগইন করা ইউজারের প্রোফাইল তথ্য এবং নির্দিষ্ট Client/Creator রোল ভিত্তিক প্রোফাইল রিটার্ন করে।",
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_user_profile(db, current_user)
    
    # Construct response dynamically based on role
    user_data = UserResponse.model_validate(current_user)
    
    if current_user.role == "client":
        profile_data = ClientProfileResponse.model_validate(profile)
    else:
        # Load relationships for creator profile to serialize correctly
        profile_data = CreatorProfileResponse.model_validate(profile)
        
    return ProfileResponse(user=user_data, profile=profile_data)


# ── 2. Update Client Profile ──────────────────────────────────
@router.put(
    "/client",
    response_model=ClientProfileResponse,
    summary="Update Client Profile",
    description="Client ইউজারের প্রোফাইল ইনফরমেশন আপডেট করে। (শুধুমাত্র Client রোলের জন্য প্রযোজ্য)",
)
def update_client(
    request: ClientProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্লায়েন্টদের জন্য অনুমোদিত (Allowed for clients only)",
        )
    profile = profile_service.update_client_profile(db, current_user, request)
    return ClientProfileResponse.model_validate(profile)


# ── 3. Update Creator Profile ─────────────────────────────────
@router.put(
    "/creator",
    response_model=CreatorProfileResponse,
    summary="Update Creator Profile",
    description="Creator ইউজারের প্রোফাইল ইনফরমেশন, ক্যাটাগরি, সোশাল লিংক এবং পোর্টফোলিও আপডেট করে।",
)
def update_creator(
    request: CreatorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CREATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="এই অ্যাকশনটি শুধুমাত্র ক্রিয়েটরদের জন্য অনুমোদিত (Allowed for creators only)",
        )
    profile = profile_service.update_creator_profile(db, current_user, request)
    return CreatorProfileResponse.model_validate(profile)


# ── 4. Toggle Security Settings ───────────────────────────────
@router.put(
    "/security",
    response_model=UserResponse,
    summary="Update Security Settings",
    description="2FA, Biometrics/Fingerprint, Face ID বা Phone OTP সেটিংস অন/অফ করে।",
)
def update_security(
    request: SecuritySettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = profile_service.update_security_settings(db, current_user, request)
    return UserResponse.model_validate(updated_user)


# ── 5. Update Avatar ──────────────────────────────────────────
@router.post(
    "/avatar",
    response_model=UserResponse,
    summary="Update User Avatar",
    description="ইউজারের প্রোফাইল পিকচার (Avatar) URL আপডেট করে।",
)
def update_user_avatar(
    request: AvatarUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = profile_service.update_avatar(db, current_user, request.avatar_url)
    return UserResponse.model_validate(updated_user)
