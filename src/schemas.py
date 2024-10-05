from pydantic import BaseModel
from typing import List
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int


class ProductRead(ProductCreate):
    id: int

    class Config:
        orm_mode = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderRead(BaseModel):
    id: int
    created_at: datetime
    status: str
    items: List[OrderItemCreate]

    class Config:
        orm_mode = True
