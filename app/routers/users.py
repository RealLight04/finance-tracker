from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["사용자"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/security")
def get_security_status(current_user: User = Depends(get_current_user)):
    return {
        "otp_enabled": current_user.otp_enabled,
        "failed_login_attempts": current_user.failed_login_attempts,
        "locked_until": current_user.locked_until,
    }
