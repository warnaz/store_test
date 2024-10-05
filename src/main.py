from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session
from . import crud, schemas


app = FastAPI()


@app.post("/products", response_model=schemas.ProductRead)
async def create_product(product: schemas.ProductCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_product(session, **product.dict())


@app.get("/products", response_model=List[schemas.ProductRead])
async def get_products(session: AsyncSession = Depends(get_session)):
    return await crud.get_products(session)


@app.get("/products/{product_id}", response_model=schemas.ProductRead)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return await crud.get_product(session, product_id)


@app.put("/products/{product_id}", response_model=schemas.ProductRead)
async def update_product(product_id: int, product: schemas.ProductCreate, session: AsyncSession = Depends(get_session)):
    return await crud.update_product(session, product_id, **product.dict())


@app.delete("/products/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return await crud.delete_product(session, product_id)


@app.post("/orders", response_model=schemas.OrderRead)
async def create_order(order: schemas.OrderCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_order(session, order.items)


@app.get("/orders", response_model=List[schemas.OrderRead])
async def get_orders(session: AsyncSession = Depends(get_session)):
    return await crud.get_orders(session)


@app.get("/orders/{order_id}", response_model=schemas.OrderRead)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    return await crud.get_order(session, order_id)


@app.patch("/orders/{order_id}/status", response_model=schemas.OrderRead)
async def update_order_status(order_id: int, status: str, session: AsyncSession = Depends(get_session)):
    return await crud.update_order_status(session, order_id, status)
