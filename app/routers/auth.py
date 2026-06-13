from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import LoginRequest, Token, UserCreate, UserRead
from app.services.auth import (
    create_access_token,
    create_user,
    get_user_by_email,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")
    return create_user(db, body.email, body.username, body.password)


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    return Token(access_token=create_access_token(user.id))
