from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    title: str
    amount: float
    type: TransactionType
    category: str
    note: Optional[str] = None
    transaction_date: date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("금액은 0보다 커야 합니다")
        return v


class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    note: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionRead(BaseModel):
    id: int
    title: str
    amount: float
    type: TransactionType
    category: str
    note: Optional[str]
    transaction_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class MonthlySummary(BaseModel):
    year: int
    month: int
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int
