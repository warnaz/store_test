import pytest
from httpx import AsyncClient
from fastapi import status
from src.main import app
from src.database import get_session
from src.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Переопределяем зависимость получения сессии для тестов
async def override_get_session() -> AsyncSession: # type: ignore
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


# Создаем и настраиваем базу данных перед запуском тестов
@pytest.fixture(autouse=True, scope="module")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Тест для создания товара
@pytest.mark.asyncio
async def test_create_product():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/products", json={
            "name": "Test Product",
            "description": "A sample product",
            "price": 10.99,
            "stock_quantity": 100
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["price"] == 10.99
        assert data["stock_quantity"] == 100


# Тест для получения списка товаров
@pytest.mark.asyncio
async def test_get_products():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/products")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0


# Тест для создания заказа и проверки наличия товара на складе
@pytest.mark.asyncio
async def test_create_order():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        product_response = await ac.post("/products", json={
            "name": "Order Product",
            "description": "A product for order",
            "price": 20.0,
            "stock_quantity": 50
        })
        assert product_response.status_code == status.HTTP_200_OK
        product_data = product_response.json()

        order_response = await ac.post("/orders", json={
            "items": [{"product_id": product_data["id"], "quantity": 10}]
        })
        assert order_response.status_code == status.HTTP_200_OK
        order_data = order_response.json()
        assert len(order_data["items"]) == 1
        assert order_data["items"][0]["quantity"] == 10

        product_check_response = await ac.get(f"/products/{product_data['id']}")
        product_check_data = product_check_response.json()
        assert product_check_data["stock_quantity"] == 40


# Тест для создания заказа с недостаточным количеством товара
@pytest.mark.asyncio
async def test_create_order_insufficient_stock():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        product_response = await ac.post("/products", json={
            "name": "Low Stock Product",
            "description": "A product with low stock",
            "price": 50.0,
            "stock_quantity": 5
        })
        assert product_response.status_code == status.HTTP_200_OK
        product_data = product_response.json()

        order_response = await ac.post("/orders", json={
            "items": [{"product_id": product_data["id"], "quantity": 10}]
        })
        assert order_response.status_code == status.HTTP_400_BAD_REQUEST
        assert order_response.json()["detail"] == f"Not enough stock for product '{product_data['name']}'. Requested: 10, Available: 5"
