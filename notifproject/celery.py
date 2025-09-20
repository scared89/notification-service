import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifproject.settings')

app = Celery('notifproject')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
