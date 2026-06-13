from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    otp_code: Optional[str] = None  # OTP 활성화된 계정은 필수


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    otp_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class OTPSetupResponse(BaseModel):
    secret: str
    qr_uri: str
    message: str


class OTPVerifyRequest(BaseModel):
    code: str
