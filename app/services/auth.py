import re
from datetime import datetime, timedelta, timezone

import bcrypt
import pyotp
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User


# ---------- 비밀번호 ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def validate_password_strength(password: str) -> str | None:
    """비밀번호 강도 검증. 문제가 있으면 오류 메시지 반환, 통과하면 None."""
    if len(password) < 8:
        return "비밀번호는 최소 8자 이상이어야 합니다"
    if not re.search(r"[A-Za-z]", password):
        return "비밀번호에 영문자를 포함해야 합니다"
    if not re.search(r"\d", password):
        return "비밀번호에 숫자를 포함해야 합니다"
    return None


# ---------- JWT ----------

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "type": "access", "exp": expire}, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return jwt.encode({"sub": str(user_id), "type": "refresh", "exp": expire}, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str, token_type: str = "access") -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != token_type:
            return None
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except JWTError:
        return None


# ---------- 유저 조회/생성 ----------

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, username: str, password: str) -> User:
    user = User(email=email, username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- 로그인 실패 / 잠금 ----------

def is_account_locked(user: User) -> bool:
    if user.locked_until and datetime.now(timezone.utc) < user.locked_until.replace(tzinfo=timezone.utc):
        return True
    return False


def record_failed_login(db: Session, user: User) -> None:
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= settings.max_login_attempts:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.lockout_minutes)
    db.commit()


def reset_failed_login(db: Session, user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()


# ---------- OTP (TOTP) ----------

def generate_otp_secret() -> str:
    return pyotp.random_base32()


def get_otp_qr_uri(user: User) -> str:
    totp = pyotp.TOTP(user.otp_secret)
    return totp.provisioning_uri(name=user.email, issuer_name="PX 가계부")


def verify_otp(user: User, code: str) -> bool:
    if not user.otp_secret:
        return False
    totp = pyotp.TOTP(user.otp_secret)
    return totp.verify(code, valid_window=1)  # ±30초 허용
