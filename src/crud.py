from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from .models import Product, Order, OrderItem, OrderStatus


async def create_product(session: AsyncSession, name: str, description: str, price: float, stock_quantity: int):
    product = Product(name=name, description=description, price=price, stock_quantity=stock_quantity)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def get_products(session: AsyncSession):
    result = await session.execute(select(Product))
    return result.scalars().all()


async def get_product(session: AsyncSession, product_id: int):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def update_product(session: AsyncSession, product_id: int, name: str, description: str, price: float, stock_quantity: int):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = name
    product.description = description
    product.price = price
    product.stock_quantity = stock_quantity
    await session.commit()
    return product


async def delete_product(session: AsyncSession, product_id: int):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await session.delete(product)
    await session.commit()


async def create_order(session: AsyncSession, items: list[dict]):
    order = Order()
    session.add(order)

    for item in items:
        product = await session.get(Product, item['product_id'])
        if not product or product.stock_quantity < item['quantity']:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        order_item = OrderItem(order=order, product=product, quantity=item['quantity'])
        session.add(order_item)
        
        product.stock_quantity -= item['quantity']
    
    await session.commit()
    await session.refresh(order)
    return order


async def get_orders(session: AsyncSession):
    result = await session.execute(select(Order))
    return result.scalars().all()


async def get_order(session: AsyncSession, order_id: int):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


async def update_order_status(session: AsyncSession, order_id: int, status: OrderStatus):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    await session.commit()
    return order
