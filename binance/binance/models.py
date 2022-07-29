from datetime import timedelta

from django.db import models


class ExchangeUpdates(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    duration = models.DurationField(default=timedelta())

    def __str__(self):
        return self.pk

    class Meta:
        abstract = True


class BankExchanges(models.Model):
    FIATS = None
    ModelUpdates = ExchangeUpdates

    from_fiats = models.CharField(max_length=3, choices=FIATS)
    to_fiats = models.CharField(max_length=3, choices=FIATS)
    price = models.FloatField(null=True, blank=True, default=None)

    def __str__(self):
        return self.price

    class Meta:
        abstract = True


class P2PExchanges(models.Model):
    ASSETS = None
    TRADE_TYPES = None
    FIATS = None
    PAY_TYPES = None

    asset = models.CharField(max_length=4, choices=ASSETS)
    fiat = models.CharField(max_length=3, choices=FIATS)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    pay_type = models.CharField(max_length=15, choices=PAY_TYPES)
    price = models.FloatField(null=True, blank=True, default=None)

    def __str__(self):
        return self.price

    class Meta:
        abstract = True
