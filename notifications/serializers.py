from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "message",
            "channel",
            "status",
            "tried_channels",
            "last_error",
            "sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "tried_channels",
            "last_error",
            "sent_at",
            "created_at",
            "updated_at",
        ]
