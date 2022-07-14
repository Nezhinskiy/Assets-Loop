from django.db import models


PAYMENT_SYSTEMS = (
    [],
    ["Tinkoff"]
)


class UsdtEur(models.Model):
    buy = models.FloatField()
    sell = models.FloatField()
    pay_types = models.CharField(max_length=10, choices=PAYMENT_SYSTEMS)
    updated = models.DateTimeField(
        'Дата обновления', auto_now_add=True, db_index=True
    )
