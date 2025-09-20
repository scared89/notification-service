from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    '''Модель уведомления'''
    CHANNEL_EMAIL = "email"
    CHANNEL_SMS = "sms"
    CHANNEL_TELEGRAM = "telegram"
    CHANNEL_ANY = "any"

    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_SMS, "SMS"),
        (CHANNEL_TELEGRAM, "Telegram"),
        (CHANNEL_ANY, "Any"),
    ]

    STATUS_NEW = "new"
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_ANY)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    tried_channels = models.JSONField(default=list, blank=True)
    last_error = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def mark_sent(self):
        self.status = self.STATUS_SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def mark_failed(self, error_text=None):
        self.status = self.STATUS_FAILED
        if error_text:
            self.last_error = error_text
        self.save(update_fields=["status", "last_error", "updated_at"])
