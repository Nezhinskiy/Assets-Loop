import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arbitration.settings")
app = Celery("arbitration")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
