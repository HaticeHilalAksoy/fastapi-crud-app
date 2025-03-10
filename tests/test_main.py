import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes import get_db

client = TestClient(app)


@pytest.fixture
def mock_db_fixture():
    """Fixture to create a mock database connection"""
    return MagicMock()


@pytest.fixture
def mock_redis_fixture():
    """Fixture to create mock Redis connection"""
    return AsyncMock()


@pytest.fixture
def task_data_fixture():
    """Fixture that generates task data for testing"""
    return {"title": "Test Task", "description": "Test task description"}


@pytest.fixture
def task_update_data_fixture():
    """Fixture that generates task update data for testing"""
    return {
        "title": "Updated Task",
        "description": "Updated task description",
        "completed": True,
    }


@pytest.fixture
def override_get_db(mock_db_fixture):
    """
    Temporarily overrides the get_db function
    and returns a mock database connection instead.
    """
    original_get_db = app.dependency_overrides.get(get_db)

    def _get_test_db():
        yield mock_db_fixture

    app.dependency_overrides[get_db] = _get_test_db
    yield

    if original_get_db:
        app.dependency_overrides[get_db] = original_get_db
    else:
        del app.dependency_overrides[get_db]


@pytest.mark.asyncio
@patch("app.routes.get_redis")
async def test_get_tasks_cached(
    mock_get_redis, _mock_redis_fixture, _mock_db_fixture, _override_get_db
):
    """Tests the functionality of fetching tasks from the cache"""
    cached_tasks = json.dumps(
        [
            {
                "id": 1,
                "title": "Cached Task",
                "description": "Cached description",
                "completed": False,
            }
        ]
    )
    _mock_redis_fixture.get.return_value = cached_tasks
    mock_get_redis.return_value.__anext__.return_value = _mock_redis_fixture

    response = client.get("/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert data["cached"]
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Cached Task"
    _mock_redis_fixture.get.assert_called_once_with("tasks_list")


@pytest.mark.asyncio
@patch("app.routes.get_redis")
async def test_get_tasks_not_cached(
    mock_get_redis, _mock_redis_fixture, _mock_db_fixture, _override_get_db
):
    """Tests the functionality of fetching non-cached tasks from the database"""
    _mock_redis_fixture.get.return_value = None
    mock_get_redis.return_value.__anext__.return_value = _mock_redis_fixture

    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Test Task"
    mock_task.description = "Test Description"
    mock_task.completed = False

    _mock_db_fixture.query.return_value.all.return_value = [mock_task]

    response = client.get("/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert not data["cached"]
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Test Task"

    _mock_db_fixture.query.assert_called_once()
    _mock_redis_fixture.setex.assert_called_once()


@pytest.mark.asyncio
@patch("app.routes.get_redis")
async def test_create_task(
    mock_get_redis,
    _mock_redis_fixture,
    _mock_db_fixture,
    _override_get_db,
    _task_data_fixture,
):
    """Tests the new task creation functionality"""
    mock_get_redis.return_value.__anext__.return_value = _mock_redis_fixture
    _mock_redis_fixture.get.return_value = json.dumps([])

    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = _task_data_fixture["title"]
    mock_task.description = _task_data_fixture["description"]
    mock_task.completed = False

    def side_effect_add(task):
        task.id = 1
        task.completed = False

    _mock_db_fixture.add.side_effect = side_effect_add

    response = client.post("/tasks/", json=_task_data_fixture)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == _task_data_fixture["title"]
    assert data["description"] == _task_data_fixture["description"]

    _mock_db_fixture.add.assert_called_once()
    _mock_db_fixture.commit.assert_called_once()
    _mock_db_fixture.refresh.assert_called_once()
    _mock_redis_fixture.setex.assert_called_once()


@pytest.mark.asyncio
@patch("app.routes.get_redis")
async def test_update_task(
    mock_get_redis,
    _mock_redis_fixture,
    _mock_db_fixture,
    _override_get_db,
    _task_update_data_fixture,
):
    """Tests the task update function"""
    task_id = 1

    mock_get_redis.return_value.__anext__.return_value = _mock_redis_fixture
    cached_tasks = json.dumps(
        [
            {
                "id": task_id,
                "title": "Old Title",
                "description": "Old Description",
                "completed": False,
            }
        ]
    )
    _mock_redis_fixture.get.return_value = cached_tasks

    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.title = "Old Title"
    mock_task.description = "Old Description"
    mock_task.completed = False

    _mock_db_fixture.query.return_value.filter.return_value.first.return_value = (
        mock_task
    )

    response = client.put(f"/tasks/{task_id}", json=_task_update_data_fixture)

    assert response.status_code == 200
    assert mock_task.title == _task_update_data_fixture["title"]
    assert mock_task.description == _task_update_data_fixture["description"]
    assert mock_task.completed == _task_update_data_fixture["completed"]

    _mock_db_fixture.commit.assert_called_once()
    _mock_db_fixture.refresh.assert_called_once()
    _mock_redis_fixture.setex.assert_called_once()
