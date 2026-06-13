from datetime import date

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import MonthlySummary, TransactionCreate, TransactionUpdate


def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    tx = Transaction(**data.model_dump(), user_id=user_id)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transactions(
    db: Session,
    user_id: int,
    tx_type: TransactionType | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Transaction]:
    q = db.query(Transaction).filter(Transaction.user_id == user_id)
    if tx_type:
        q = q.filter(Transaction.type == tx_type)
    if category:
        q = q.filter(Transaction.category == category)
    if start_date:
        q = q.filter(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.filter(Transaction.transaction_date <= end_date)
    return q.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


def get_transaction(db: Session, user_id: int, tx_id: int) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user_id).first()


def update_transaction(db: Session, tx: Transaction, data: TransactionUpdate) -> Transaction:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, tx: Transaction) -> None:
    db.delete(tx)
    db.commit()


def get_monthly_summary(db: Session, user_id: int, year: int, month: int) -> MonthlySummary:
    rows = (
        db.query(Transaction.type, func.sum(Transaction.amount), func.count(Transaction.id))
        .filter(
            Transaction.user_id == user_id,
            extract("year", Transaction.transaction_date) == year,
            extract("month", Transaction.transaction_date) == month,
        )
        .group_by(Transaction.type)
        .all()
    )

    total_income = 0.0
    total_expense = 0.0
    total_count = 0
    for tx_type, amount, count in rows:
        if tx_type == TransactionType.income:
            total_income = float(amount)
        else:
            total_expense = float(amount)
        total_count += count

    return MonthlySummary(
        year=year,
        month=month,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        transaction_count=total_count,
    )
