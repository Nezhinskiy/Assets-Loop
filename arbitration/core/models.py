from datetime import timedelta

from django.db import models


class UpdatesModel(models.Model):
    """
    Creates an abstract model to store the date and time of the last update.
    """
    updated = models.DateTimeField(
        verbose_name='Update date',
        auto_now_add=True,
        db_index=True
    )
    duration = models.DurationField(default=timedelta())

    class Meta:
        abstract = True


class InfoLoop(models.Model):
    """
    Creates a model to store data about the launch and run time of the
    application.
    """
    value = models.BooleanField(default=False)
    started = models.DateTimeField(
        verbose_name='Started date',
        auto_now_add=True
    )
    stopped = models.DateTimeField(
        verbose_name='Stopped date',
        blank=True,
        null=True
    )
    duration = models.DurationField(default=timedelta())

    class Meta:
        ordering = ['-started']
