"""
Brand Bridge — Shared Dependencies
get_current_user: Extracts and validates JWT from Authorization header.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# Bearer token scheme — shows lock icon in Swagger UI
security_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="JWT Bearer Token — login করার পর token পাবেন",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts the current authenticated user
    from the JWT Bearer token.

    Usage in routes:
        @router.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            return {"user": user.name}
    """
    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="টোকেন অবৈধ বা মেয়াদ শেষ (Invalid or expired token)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="টোকেনে ইউজার তথ্য নেই (Token missing user info)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ইউজার পাওয়া যায়নি (User not found)",
        )

    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="অ্যাকাউন্ট মুছে ফেলা হয়েছে (Account deleted)",
        )

    return user
