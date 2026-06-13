from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import LoginRequest, OTPSetupResponse, OTPVerifyRequest, Token, UserCreate, UserRead
from app.services.auth import (
    create_access_token,
    create_refresh_token,
    create_user,
    decode_token,
    generate_otp_secret,
    get_otp_qr_uri,
    get_user_by_email,
    get_user_by_id,
    is_account_locked,
    record_failed_login,
    reset_failed_login,
    validate_password_strength,
    verify_otp,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)):
    error = validate_password_strength(body.password)
    if error:
        raise HTTPException(status_code=400, detail=error)
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")
    return create_user(db, body.email, body.username, body.password)


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 올바르지 않습니다")

    if is_account_locked(user):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"로그인 시도가 너무 많습니다. {user.locked_until.strftime('%H:%M')}에 다시 시도하세요")

    if not verify_password(body.password, user.hashed_password):
        record_failed_login(db, user)
        remaining = max(0, 5 - user.failed_login_attempts)
        msg = f"비밀번호가 올바르지 않습니다" + (f" (남은 시도: {remaining}회)" if remaining > 0 else " — 계정이 잠겼습니다")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    if user.otp_enabled:
        if not body.otp_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="OTP 코드가 필요합니다")
        if not verify_otp(user, body.otp_code):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP 코드가 올바르지 않습니다")

    reset_failed_login(db, user)
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    user_id = decode_token(refresh_token, token_type="refresh")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 리프레시 토큰입니다")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다")
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/otp/setup", response_model=OTPSetupResponse)
def otp_setup(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.otp_enabled:
        raise HTTPException(status_code=400, detail="OTP가 이미 활성화되어 있습니다")
    current_user.otp_secret = generate_otp_secret()
    db.commit()
    db.refresh(current_user)
    return OTPSetupResponse(
        secret=current_user.otp_secret,
        qr_uri=get_otp_qr_uri(current_user),
        message="Google Authenticator 앱에서 QR 코드를 스캔하거나 secret 키를 직접 입력하세요. 설정 후 /auth/otp/verify 로 OTP 코드를 검증해야 활성화됩니다.",
    )


@router.post("/otp/verify")
def otp_verify(body: OTPVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.otp_secret:
        raise HTTPException(status_code=400, detail="먼저 /auth/otp/setup 을 호출하세요")
    if not verify_otp(current_user, body.code):
        raise HTTPException(status_code=400, detail="OTP 코드가 올바르지 않습니다. 앱의 현재 코드를 입력하세요")
    current_user.otp_enabled = True
    db.commit()
    return {"message": "OTP 2단계 인증이 활성화되었습니다. 다음 로그인부터 OTP 코드가 필요합니다."}


@router.delete("/otp/disable")
def otp_disable(body: OTPVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.otp_enabled:
        raise HTTPException(status_code=400, detail="OTP가 활성화되어 있지 않습니다")
    if not verify_otp(current_user, body.code):
        raise HTTPException(status_code=400, detail="OTP 코드가 올바르지 않습니다")
    current_user.otp_enabled = False
    current_user.otp_secret = None
    db.commit()
    return {"message": "OTP가 비활성화되었습니다"}
