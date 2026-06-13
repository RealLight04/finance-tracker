from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.transaction import MonthlySummary, TransactionCreate, TransactionRead, TransactionUpdate
from app.services.transaction import (
    create_transaction,
    delete_transaction,
    get_monthly_summary,
    get_transaction,
    get_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["거래 내역"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def add_transaction(
    body: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_transaction(db, current_user.id, body)


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    type: Optional[TransactionType] = Query(None, description="income 또는 expense"),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transactions(db, current_user.id, type, category, start_date, end_date, skip, limit)


@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_monthly_summary(db, current_user.id, year, month)


@router.get("/{tx_id}", response_model=TransactionRead)
def get_one(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = get_transaction(db, current_user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return tx


@router.patch("/{tx_id}", response_model=TransactionRead)
def edit_transaction(
    tx_id: int,
    body: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = get_transaction(db, current_user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return update_transaction(db, tx, body)


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = get_transaction(db, current_user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    delete_transaction(db, tx)
