from pydantic import BaseModel


class ProductRead(BaseModel):
    id: int
    name: str
    price: int
    category: str

    model_config = {"from_attributes": True}
