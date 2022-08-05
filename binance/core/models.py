from datetime import timedelta

from django.db import models


class UpdatesModel(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    duration = models.DurationField(default=timedelta())

    class Meta:
        abstract = True
