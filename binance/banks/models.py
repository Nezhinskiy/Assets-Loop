from binance.models import ExchangeUpdates, BankExchanges
from django.db import models


FIATS_TINKOFF = (
    ('RUB', 'Rub'),
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
)


class TinkoffUpdates(ExchangeUpdates):
    pass


class TinkoffExchanges(BankExchanges):
    FIATS = FIATS_TINKOFF
    update = models.ForeignKey(
        TinkoffUpdates, related_name='%(class)s', on_delete=models.CASCADE
    )
