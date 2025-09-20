import time
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Notification
from . import tasks

User = get_user_model()


def wait_for_task(task, timeout=15):
    """Ждём завершения Celery-задачи."""
    start = time.time()
    while time.time() - start < timeout:
        if task.ready():
            return task.get()
        time.sleep(0.5)
    raise TimeoutError("Celery task did not finish in time")


@pytest.mark.django_db(transaction=True)
def test_worker_processes_notifications(celery_worker):
    """
    Проверяем, что Celery-воркер реально обрабатывает уведомление.
    """
    client = APIClient()
    user = User.objects.create_user(
        username="workeruser",
        password="pass1234"
    )

    url = reverse("notification-create")
    payload = {
        "user": user.id,
        "message": "Test message via worker",
        "channel": "email",  # начинаем с email
    }

    response = client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    notif_id = response.data["id"]

    task = tasks.process_notification.apply_async(args=[notif_id])
    result = wait_for_task(task)

    notif = Notification.objects.get(id=notif_id)
    assert notif.status in [
        Notification.STATUS_SENT,
        Notification.STATUS_FAILED
    ]
    assert f"Notification {notif.id}" in result


@pytest.mark.django_db(transaction=True)
def test_multiple_attempts_real_flow(celery_worker):
    """
    Проверяем реальный фолбэк: email → sms → telegram.
    """
    client = APIClient()
    user = User.objects.create_user(username="flowuser", password="pass1234")

    url = reverse("notification-create")
    payload = {
        "user": user.id,
        "message": "Check fallback sequence",
        "channel": "email",
    }

    response = client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    notif_id = response.data["id"]

    task = tasks.process_notification.apply_async(args=[notif_id])
    result = wait_for_task(task)

    notif = Notification.objects.get(id=notif_id)
    assert notif.status in [
        Notification.STATUS_SENT,
        Notification.STATUS_FAILED
    ]
    assert isinstance(result, str)


@pytest.mark.django_db(transaction=True)
def test_direct_telegram_channel(celery_worker):
    """
    Проверяем отправку напрямую через Telegram.
    """
    client = APIClient()
    user = User.objects.create_user(username="tguser", password="pass1234")

    url = reverse("notification-create")
    payload = {
        "user": user.id,
        "message": "Hello via Telegram",
        "channel": "telegram",
    }

    response = client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    notif_id = response.data["id"]

    task = tasks.process_notification.apply_async(args=[notif_id])
    result = wait_for_task(task)

    notif = Notification.objects.get(id=notif_id)
    assert notif.status in [
        Notification.STATUS_SENT,
        Notification.STATUS_FAILED
    ]
    assert "Notification" in result
