import pytest
from celery.contrib.testing.worker import start_worker


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "redis://redis:6379/0",
        "result_backend": "redis://redis:6379/0",
        "task_always_eager": False,
    }


@pytest.fixture(scope="session")
def celery_includes():
    return ["notifications.tasks"]


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {
        "queues": ("celery",),
        "perform_ping_check": False,
    }


@pytest.fixture(scope="session")
def celery_worker(celery_session_app, celery_worker_parameters):
    """
    Запускаем один реальный воркер на всю сессию тестов.
    Используем Postgres/Redis, поэтому mark.django_db ставим с transaction=True.
    """
    with start_worker(celery_session_app, **celery_worker_parameters):
        yield
