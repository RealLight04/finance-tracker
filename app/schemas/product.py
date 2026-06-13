from typing import Optional

from pydantic import BaseModel


class ProductRead(BaseModel):
    id: int
    name: str
    price: int
    category: str

    model_config = {"from_attributes": True}


class ProductUpdate(BaseModel):
    price: Optional[int] = None
    category: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    price: int
    category: str
