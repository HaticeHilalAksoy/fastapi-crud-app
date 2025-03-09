from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app

client = TestClient(app)


def test_read_main():
    """Ana endpoint'i test eder."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# PostgreSQL ve Redis bağlantısını mock etmek için
@pytest.mark.asyncio
@patch("app.routes.get_db")
@patch("app.database.get_redis")
async def test_health_check_with_mocks(mock_get_redis, mock_get_db):
    # Mock redis ve db objelerini hazırla
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True

    mock_db = AsyncMock()

    # Mock fonksiyonları yapılandır
    mock_get_redis.return_value.__aiter__.return_value = [mock_redis]
    mock_get_db.return_value.__aiter__.return_value = [mock_db]

    # Test et
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
