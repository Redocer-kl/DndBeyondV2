# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.tasks import celery_app

@pytest.fixture(scope="session", autouse=True)
def configure_test_celery():
    """
    Включаем режим 'always_eager' и разрешаем сохранение результатов выполненных задач.
    """
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_store_eager_result=True,  
        cache_backend="memory",
        beat_schedule={},
    )

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c