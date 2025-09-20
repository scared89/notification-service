from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer
from .tasks import process_notification


class NotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        notif = serializer.save(
            status=Notification.STATUS_NEW,
            tried_channels=[]
        )
        process_notification.delay(notif.id)
