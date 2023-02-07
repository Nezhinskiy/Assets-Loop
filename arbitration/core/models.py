from datetime import timedelta

from django.db import models


class UpdatesModel(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    duration = models.DurationField(default=timedelta())

    class Meta:
        abstract = True


class InfoLoop(models.Model):
    value = models.BooleanField(null=True, blank=True, default=None)
    updated = models.DateTimeField(
        'Update date', auto_now_add=True
    )
    all_banks_exchanges = models.DurationField(default=timedelta())
    all_crypto_exchanges = models.DurationField(default=timedelta())
    all_exchanges = models.DurationField(default=timedelta())
    start_banks_exchanges = models.DateTimeField(
        null=True, blank=True, default=None
    )
    start_crypto_exchanges = models.DateTimeField(
        null=True, blank=True, default=None
    )
    start_all_exchanges = models.DateTimeField(
        null=True, blank=True, default=None
    )
