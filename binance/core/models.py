from datetime import timedelta

from django.db import models


class ExchangeUpdatesModel(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    duration = models.DurationField(default=timedelta())

    # def __str__(self):
    #     return self.pk

    class Meta:
        abstract = True


class BankExchangesModel(models.Model):
    FIATS = None

    # updated = models.DateTimeField('Update date', null=True, blank=True)
    from_fiat = models.CharField(max_length=3, choices=FIATS)
    to_fiat = models.CharField(max_length=3, choices=FIATS)
    price = models.FloatField(null=True, blank=True, default=None)

    # def __str__(self):
    #     return str(self.price)

    class Meta:
        abstract = True


class P2PExchangesModel(models.Model):
    ASSETS = None
    TRADE_TYPES = None
    FIATS = None
    PAY_TYPES = None

    asset = models.CharField(max_length=4, choices=ASSETS)
    fiat = models.CharField(max_length=3, choices=FIATS)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    pay_type = models.CharField(max_length=16, choices=PAY_TYPES)
    price = models.FloatField(null=True, blank=True, default=None)

    # def __str__(self):
    #     return self.price

    class Meta:
        abstract = True
