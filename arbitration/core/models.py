from datetime import timedelta, datetime

from django.db import models


class UpdatesModel(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    duration = models.DurationField(default=timedelta())

    class Meta:
        abstract = True


class InfoLoop(models.Model):
    value = models.BooleanField(default=False)
    started = models.DateTimeField('Started date', auto_now_add=True)
    stopped = models.DateTimeField('Stopped date', blank=True)
    duration = models.DurationField(default=timedelta())

    class Meta:
        ordering = ['-started']
