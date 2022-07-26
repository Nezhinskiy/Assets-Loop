# from django.contrib.auth import get_user_model
from datetime import timedelta

from django.db import models

ASSETS = (
    ('USDT', 'USDT'),
    ('BUSD', 'BUSD'),
    ('BTC', 'BTC'),
    ('ETH', 'ETH'),
)
TRADE_TYPES = (
    ('BUY', 'buy'),
    ('SELL', 'sell')
)
FIATS = (
    ('RUB', 'rub'),
    ('USD', 'usd'),
    ('EUR', 'eur'),
    ('GBP', 'gbp'),
)
PAY_TYPES = (
    ('Tinkoff', 'Tinkoff'),
    ('Wise', 'Wise'),
    # 'TBCbank',
    # 'BankofGeorgia',
    ('RosBank', 'RosBank'),
    # ('RUBfiatbalance', 'RUBfiatbalance')
)


class UpdateP2PBinance(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    duration = models.DurationField(default=timedelta())

    def __str__(self):
        return self.pk


class P2PBinance(models.Model):
    asset = models.CharField(max_length=4, choices=ASSETS)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    fiat = models.CharField(max_length=3, choices=FIATS)
    pay_type = models.CharField(max_length=15, choices=PAY_TYPES)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
         UpdateP2PBinance, related_name='datas', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.price
