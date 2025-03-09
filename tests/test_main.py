import os

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.main import app
from app.redis_client import get_redis

client = TestClient(app)

# Çevre değişkenlerinden bağlantı bilgilerini al
# Bu şekilde hem local hem de CI ortamında çalışacak
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost:5432/fastapi_crud"
)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Test database engine
test_engine = create_async_engine(DATABASE_URL)


@pytest.mark.asyncio
async def test_postgres_connection():
    """PostgreSQL bağlantısını test eder."""
    try:
        async with AsyncSession(test_engine) as session:
            result = await session.execute("SELECT 1")
            assert result.scalar() == 1
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")


@pytest.mark.asyncio
async def test_redis_connection():
    """Redis bağlantısını test eder."""
    # Redis client'ı doğrudan oluştur
    redis_client = Redis.from_url(REDIS_URL)

    try:
        assert await redis_client.ping() is True
    except Exception as e:
        pytest.fail(f"Redis connection failed: {e}")
    finally:
        await redis_client.close()


@pytest.mark.asyncio
async def test_full_health_check():
    """Hem DB hem Redis bağlantısını /health endpoint'i üzerinden test eder."""

    # Override the get_redis dependency in app to use our test URL
    async def override_get_redis():
        redis_client = Redis.from_url(REDIS_URL)
        yield redis_client
        await redis_client.close()

    # Override the dependency for testing
    app.dependency_overrides[get_redis] = override_get_redis

    # Use AsyncClient for async endpoint testing
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    # Reset dependency override
    app.dependency_overrides = {}
