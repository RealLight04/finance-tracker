from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductRead

router = APIRouter(prefix="/products", tags=["PX 상품"])


@router.get("", response_model=list[ProductRead])
def search_products(
    q: Optional[str] = Query(None, description="상품명 검색어"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if q:
        query = query.filter(Product.name.contains(q))
    if category:
        query = query.filter(Product.category == category)
    return query.order_by(Product.name).limit(30).all()


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).distinct().order_by(Product.category).all()
    return [r[0] for r in rows]
