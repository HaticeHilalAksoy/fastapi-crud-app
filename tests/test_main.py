import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, get_redis
from app.main import app

client = TestClient(app)


def test_postgres_connection():
    """PostgreSQL veritabanına bağlantıyı test eder."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")


@pytest.mark.asyncio
async def test_redis_connection():
    """Redis bağlantısını test eder."""
    try:
        redis_client = await anext(get_redis())
        pong = await redis_client.ping()
        assert pong is True
        print("✅ Redis connection successful")
    except Exception as e:
        pytest.fail(f"Redis connection failed: {e}")


@pytest.mark.asyncio
async def test_full_health_check():
    """Hem DB hem Redis bağlantısını /health endpoint'i üzerinden test eder."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    redis_client = await anext(get_redis())
    assert await redis_client.ping() is True

    with Session(engine) as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
