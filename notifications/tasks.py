import time
from celery import shared_task
from django.utils import timezone
from .models import Notification
from . import channels

# сколько раз пробовать на каждом канале
MAX_RETRIES_PER_CHANNEL = 3
# задержка в секундах между попытками
RETRY_BACKOFF = 2

CHANNEL_SENDERS = {
    Notification.CHANNEL_EMAIL: channels.send_email,
    Notification.CHANNEL_SMS: channels.send_sms,
    Notification.CHANNEL_TELEGRAM: channels.send_telegram,
}


@shared_task(bind=True)
def process_notification(self, notification_id):
    """Основная таска: отправка с fallback и ретраями"""
    try:
        notif = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"

    notif.status = Notification.STATUS_PENDING
    notif.save(update_fields=["status", "updated_at"])

    tried_logs = []

    # если канал "любой" — пробуем все
    if notif.channel == Notification.CHANNEL_ANY:
        channels_to_try = [
            Notification.CHANNEL_EMAIL,
            Notification.CHANNEL_SMS,
            Notification.CHANNEL_TELEGRAM,
        ]
    else:
        channels_to_try = [notif.channel]

    # идём по каналам
    for ch in channels_to_try:
        sender = CHANNEL_SENDERS[ch]

        for attempt in range(1, MAX_RETRIES_PER_CHANNEL + 1):
            try:
                ok, err = sender(notif)

                tried_logs.append({
                    "channel": ch,
                    "status": "ok" if ok else "error",
                    "error": err,
                    "attempt": attempt,
                })

                if ok:
                    notif.tried_channels = tried_logs
                    notif.status = Notification.STATUS_SENT
                    notif.sent_at = timezone.now()
                    notif.save(update_fields=["tried_channels", "status", "sent_at", "updated_at"])
                    return f"Notification {notif.id} sent via {ch} (attempt {attempt})"

                # если канал вернул fail — пробуем ещё раз
                notif.tried_channels = tried_logs
                notif.last_error = err
                notif.save(update_fields=["tried_channels", "last_error", "updated_at"])

            except Exception as exc:
                # защита от крэша канала
                tried_logs.append({
                    "channel": ch,
                    "status": "exception",
                    "error": str(exc),
                    "attempt": attempt,
                })
                notif.tried_channels = tried_logs
                notif.last_error = str(exc)
                notif.save(update_fields=["tried_channels", "last_error", "updated_at"])

            # ждём перед следующей попыткой
            if attempt < MAX_RETRIES_PER_CHANNEL:
                delay = RETRY_BACKOFF ** attempt
                time.sleep(delay)

        # если канал исчерпал все попытки → переходим к следующему
        continue

    # если дошли сюда — все каналы упали
    notif.status = Notification.STATUS_FAILED
    notif.last_error = "All channels failed"
    notif.tried_channels = tried_logs
    notif.save(update_fields=["status", "last_error", "tried_channels", "updated_at"])
    return f"Notification {notif.id} failed after retries"
