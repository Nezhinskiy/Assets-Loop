from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


PAYMENT_SYSTEMS = (
    ('', ''),
    ('Tinkoff', 'Tinkoff'),
    ('Wise', 'Wise'),
)


class UsdtEur(models.Model):
    buy = models.FloatField()
    sell = models.FloatField()
    pay_types = models.CharField(max_length=10, choices=PAYMENT_SYSTEMS)
    updated = models.DateTimeField(
        'Дата обновления', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.updated


class UsdtRub(models.Model):
    buy = models.FloatField()
    sell = models.FloatField()
    pay_types = models.CharField(max_length=10, choices=PAYMENT_SYSTEMS)
    updated = models.DateTimeField(
        'Дата обновления', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.updated
